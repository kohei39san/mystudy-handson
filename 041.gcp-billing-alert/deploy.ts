import dotenv from "dotenv";
import { ConfigClient } from "@google-cloud/config";
import { Storage } from "@google-cloud/storage";
import archiver from "archiver";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";

interface DeploymentConfig {
  projectId: string;
  location: string;
  deploymentName: string;
  tfDir: string;
  serviceAccount: string;
  envFile?: string;
}

// Google Cloud protobuf Value 型の interface
interface IValue {
  nullValue?: number;
  numberValue?: number;
  stringValue?: string;
  boolValue?: boolean;
  structValue?: { fields?: Record<string, IValue> };
  listValue?: { values?: IValue[] };
}

type TerraformInputValues = Record<string, { inputValue: IValue }>;

/**
 * Infrastructure Manager APIを使用してTerraformデプロイメントを作成・適用
 */
async function deployWithInfrastructureManager(
  config: DeploymentConfig
): Promise<void> {
  const client = new ConfigClient();

  // プロジェクトのロケーション取得
  const parent = client.locationPath(config.projectId, config.location);

  console.log(`Deploying to: ${parent}`);
  console.log(`Deployment Name: ${config.deploymentName}`);

  const envFilePath = config.envFile || path.join(__dirname, ".env");
  const dotenvResult = dotenv.config({ path: envFilePath });
  const dotenvError = dotenvResult.error as NodeJS.ErrnoException | undefined;
  if (dotenvError && dotenvError.code !== "ENOENT") {
    throw dotenvError;
  }

  let gcsSource = requireEnv("GCS_SOURCE_URI");
  const autoUploadTerraform = toBoolean(
    process.env.AUTO_UPLOAD_TERRAFORM,
    false
  );

  if (autoUploadTerraform) {
    gcsSource = await createAndUploadTerraformZip(config.tfDir, gcsSource);
  }

  const inputValues = buildInputValues(process.env as Record<
    string,
    string | undefined
  >);

  // デプロイメント設定を構築
  const deploymentRequest = {
    parent: parent,
    deploymentId: config.deploymentName,
    deployment: {
      serviceAccount: config.serviceAccount,
      terraformBlueprint: {
        inputValues,
        gcsSource,
      },
      artifactsGcsBucket: process.env.ARTIFACTS_GCS_BUCKET,
      labels: {
        environment: "production",
        managed_by: "terraform",
      },
    },
  };

  try {
    console.log("\n📝 デプロイメントを作成中...");
    const createResult = await client.createDeployment(deploymentRequest);
    const operation = createResult[0];

    console.log(
      `✓ デプロイメント作成リクエストが送信されました: ${operation.name}`
    );

    // オペレーション完了を待機
    const [deployment] = await operation.promise();
    console.log(`✓ デプロイメントが作成されました: ${deployment.name}`);
  } catch (error) {
    console.error("❌ デプロイメント作成エラー:", error);
    throw error;
  }
}

/**
 * デプロイメント状態を確認
 */
async function checkDeploymentStatus(
  projectId: string,
  location: string,
  deploymentName: string
): Promise<void> {
  const client = new ConfigClient();

  try {
    const deploymentPath = client.deploymentPath(
      projectId,
      location,
      deploymentName
    );

    const [deployment] = await client.getDeployment({
      name: deploymentPath,
    });

    console.log("\n📊 デプロイメント状態:");
    console.log(`  名前: ${deployment.name}`);
    console.log(`  状態: ${deployment.state}`);
    console.log(`  作成日: ${deployment.createTime}`);
    console.log(`  更新日: ${deployment.updateTime}`);

    if (deployment.latestRevision) {
      console.log(`  最新リビジョン: ${deployment.latestRevision}`);
    }
  } catch (error) {
    console.error("❌ デプロイメント状態確認エラー:", error);
    throw error;
  }
}

/**
 * 必須環境変数を取得する
 */
function requireEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`${name} が必要です`);
  }

  return value;
}

/**
 * Infrastructure Manager が要求する serviceAccount 形式に正規化する
 */
function normalizeServiceAccount(projectId: string, value: string): string {
  if (value.startsWith("projects/")) {
    return value;
  }

  return `projects/${projectId}/serviceAccounts/${value}`;
}

/**
 * 文字列を真偽値に変換する
 */
function toBoolean(value: string | undefined, defaultValue: boolean): boolean {
  if (!value) {
    return defaultValue;
  }

  const normalized = value.trim().toLowerCase();
  return ["1", "true", "yes", "on"].includes(normalized);
}

/**
 * Terraformファイルをzip化してCloud Storageにアップロードする
 */
async function createAndUploadTerraformZip(
  tfDir: string,
  gcsSourceUri: string
): Promise<string> {
  if (!fs.existsSync(tfDir)) {
    throw new Error(`TF_DIR が存在しません: ${tfDir}`);
  }

  const { bucketName, objectPath } = parseGcsUri(gcsSourceUri);
  const zipFilePath = path.join(
    os.tmpdir(),
    `terraform-${Date.now()}-${Math.random().toString(16).slice(2)}.zip`
  );

  console.log(`\n📦 Terraform zip を作成中: ${zipFilePath}`);
  await createTerraformZip(tfDir, zipFilePath);

  console.log(`☁️  Cloud Storage へアップロード中: ${gcsSourceUri}`);
  const storage = new Storage();
  await storage.bucket(bucketName).upload(zipFilePath, {
    destination: objectPath,
    contentType: "application/zip",
  });

  fs.unlinkSync(zipFilePath);
  console.log(`✓ アップロード完了: ${gcsSourceUri}`);

  return gcsSourceUri;
}

/**
 * Terraform関連ファイルをzip化する
 */
async function createTerraformZip(tfDir: string, zipFilePath: string): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    const output = fs.createWriteStream(zipFilePath);
    const archive = archiver("zip", { zlib: { level: 9 } });

    output.on("close", () => resolve());
    output.on("error", (error: Error) => reject(error));
    archive.on("error", (error: Error) => reject(error));

    archive.pipe(output);
    archive.glob("**/*.tf", { cwd: tfDir });
    archive.glob("**/*.tf.json", { cwd: tfDir });
    archive.glob("**/*.tftpl", { cwd: tfDir });
    archive.glob(".terraform.lock.hcl", { cwd: tfDir });
    archive.finalize();
  });
}

/**
 * gs:// URI をパースする
 */
function parseGcsUri(uri: string): { bucketName: string; objectPath: string } {
  if (!uri.startsWith("gs://")) {
    throw new Error(`GCS_SOURCE_URI は gs:// で始めてください: ${uri}`);
  }

  const withoutScheme = uri.slice("gs://".length);
  const firstSlash = withoutScheme.indexOf("/");
  if (firstSlash === -1) {
    throw new Error(`GCS_SOURCE_URI はオブジェクトパスまで指定してください: ${uri}`);
  }

  const bucketName = withoutScheme.slice(0, firstSlash);
  const objectPath = withoutScheme.slice(firstSlash + 1);
  if (!bucketName || !objectPath) {
    throw new Error(`GCS_SOURCE_URI が不正です: ${uri}`);
  }

  return { bucketName, objectPath };
}

/**
 * JavaScriptの値をGoogle Cloud protobuf Value型に変換する
 */
function convertToValue(value: any): IValue {
  if (value === null || value === undefined) {
    return { nullValue: 0 };
  } else if (typeof value === "string") {
    return { stringValue: value };
  } else if (typeof value === "number") {
    return { numberValue: value };
  } else if (typeof value === "boolean") {
    return { boolValue: value };
  } else if (Array.isArray(value)) {
    return {
      listValue: {
        values: value.map((v) => convertToValue(v)),
      },
    };
  } else if (typeof value === "object") {
    return {
      structValue: {
        fields: Object.fromEntries(
          Object.entries(value).map(([k, v]) => [k, convertToValue(v)])
        ),
      },
    };
  }
  return { nullValue: 0 };
}

/**
 * Terraform input variable values を .env から構築する
 */
function buildInputValues(
  env: Record<string, string | undefined>
): TerraformInputValues {
  const projectId = env.TF_PROJECT_ID || env.GCP_PROJECT_ID;
  const billingAccountId = env.TF_BILLING_ACCOUNT_ID;
  const alertEmailAddresses = parseStringList(env.TF_ALERT_EMAIL_ADDRESSES);

  if (!projectId) {
    throw new Error("TF_PROJECT_ID または GCP_PROJECT_ID が必要です");
  }

  if (!billingAccountId) {
    throw new Error("TF_BILLING_ACCOUNT_ID が必要です");
  }

  if (alertEmailAddresses.length === 0) {
    throw new Error("TF_ALERT_EMAIL_ADDRESSES が必要です");
  }

  const inputValues: TerraformInputValues = {
    project_id: { inputValue: convertToValue(projectId) },
    billing_account_id: { inputValue: convertToValue(billingAccountId) },
    alert_email_addresses: { inputValue: convertToValue(alertEmailAddresses) },
  };

  if (env.TF_BUDGET_AMOUNT) {
    inputValues.budget_amount = {
      inputValue: convertToValue(parseNumber(env.TF_BUDGET_AMOUNT, "TF_BUDGET_AMOUNT")),
    };
  }

  if (env.TF_CURRENCY_CODE) {
    inputValues.currency_code = { inputValue: convertToValue(env.TF_CURRENCY_CODE) };
  }

  if (env.TF_BUDGET_DISPLAY_NAME) {
    inputValues.budget_display_name = { inputValue: convertToValue(env.TF_BUDGET_DISPLAY_NAME) };
  }

  const alertThresholdPercentages = parseNumberList(
    env.TF_ALERT_THRESHOLD_PERCENTAGES
  );
  if (alertThresholdPercentages.length > 0) {
    inputValues.alert_threshold_percentages = {
      inputValue: convertToValue(alertThresholdPercentages),
    };
  }

  if (env.TF_REGION) {
    inputValues.region = { inputValue: convertToValue(env.TF_REGION) };
  }

  return inputValues;
}

/**
 * 文字列リストをパースする
 */
function parseStringList(value: string | undefined): string[] {
  if (!value) {
    return [];
  }

  const trimmedValue = value.trim();
  if (!trimmedValue) {
    return [];
  }

  if (trimmedValue.startsWith("[")) {
    const parsed = JSON.parse(trimmedValue);
    if (!Array.isArray(parsed)) {
      throw new Error("文字列リストは配列形式で指定してください");
    }

    return parsed.map((item: unknown) => String(item));
  }

  return trimmedValue
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

/**
 * 数値をパースする
 */
function parseNumber(value: string, name: string): number {
  const parsed = Number(value);
  if (Number.isNaN(parsed)) {
    throw new Error(`${name} は数値で指定してください`);
  }

  return parsed;
}

/**
 * 数値リストをパースする
 */
function parseNumberList(value: string | undefined): number[] {
  if (!value) {
    return [];
  }

  const trimmedValue = value.trim();
  if (!trimmedValue) {
    return [];
  }

  if (trimmedValue.startsWith("[")) {
    const parsed = JSON.parse(trimmedValue);
    if (!Array.isArray(parsed)) {
      throw new Error("数値リストは配列形式で指定してください");
    }

    return parsed.map((item: unknown) => {
      const parsedNumber = Number(item);
      if (Number.isNaN(parsedNumber)) {
        throw new Error("数値リストには数値のみ指定できます");
      }

      return parsedNumber;
    });
  }

  return trimmedValue
    .split(",")
    .map((item) => Number(item.trim()))
    .filter((item) => !Number.isNaN(item));
}

/**
 * デプロイメントを削除
 */
async function destroyDeployment(
  projectId: string,
  location: string,
  deploymentName: string
): Promise<void> {
  const client = new ConfigClient();

  try {
    console.log(`\n🗑️  デプロイメントを削除中: ${deploymentName}`);

    const deploymentPath = client.deploymentPath(
      projectId,
      location,
      deploymentName
    );

    const [operation] = await client.deleteDeployment({
      name: deploymentPath,
    });

    console.log(`✓ 削除リクエストが送信されました: ${operation.name}`);

    // 削除完了を待機
    await operation.promise();
    console.log(`✓ デプロイメントが削除されました`);
  } catch (error) {
    console.error("❌ デプロイメント削除エラー:", error);
    throw error;
  }
}

/**
 * メイン処理
 */
async function main(): Promise<void> {
  // .env を先に読み込み、以降の process.env 参照に反映する
  const envFile = process.env.ENV_FILE || path.join(__dirname, ".env");
  const dotenvResult = dotenv.config({ path: envFile });
  const dotenvError = dotenvResult.error as NodeJS.ErrnoException | undefined;
  if (dotenvError && dotenvError.code !== "ENOENT") {
    throw dotenvError;
  }

  // 環境変数またはコマンドライン引数から設定を読み込む
  const projectId = process.env.GCP_PROJECT_ID || "your-project-id";
  const location = process.env.GCP_LOCATION || "us-central1";
  const deploymentName =
    process.env.DEPLOYMENT_NAME || "gcp-billing-alert-deployment";
  const tfDir = process.env.TF_DIR || __dirname;
  const serviceAccountRaw = process.env.GCP_SERVICE_ACCOUNT?.trim();

  if (projectId === "your-project-id") {
    throw new Error(
      "GCP_PROJECT_ID が未設定です。.env の GCP_PROJECT_ID を実際のプロジェクトIDに設定してください"
    );
  }

  if (!serviceAccountRaw) {
    throw new Error(
      "GCP_SERVICE_ACCOUNT が未設定です。.env に Infrastructure Manager が実行に使用するサービスアカウントを設定してください"
    );
  }

  const serviceAccount = normalizeServiceAccount(projectId, serviceAccountRaw);

  const config: DeploymentConfig = {
    projectId,
    location,
    deploymentName,
    tfDir,
    serviceAccount,
    envFile,
  };

  // コマンド引数を処理
  const command = process.argv[2] || "deploy";

  try {
    switch (command) {
      case "deploy":
        console.log("🌍 Google Cloud Infrastructure Manager にデプロイ中...\n");
        await deployWithInfrastructureManager(config);
        console.log("\n✅ デプロイが完了しました！");
        break;

      case "status":
        await checkDeploymentStatus(
          config.projectId,
          config.location,
          config.deploymentName
        );
        break;

      case "destroy":
        await destroyDeployment(
          config.projectId,
          config.location,
          config.deploymentName
        );
        break;

      default:
        console.log(`❌ 不明なコマンド: ${command}`);
        console.log("使用方法: ts-node deploy.ts [deploy|status|destroy]");
        process.exit(1);
    }
  } catch (error) {
    console.error("エラーが発生しました:", error);
    process.exit(1);
  }
}

main();
