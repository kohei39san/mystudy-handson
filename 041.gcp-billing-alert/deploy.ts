import { ConfigServiceClient } from "@google-cloud/infra-manager";
import * as fs from "fs";
import * as path from "path";

interface DeploymentConfig {
  projectId: string;
  location: string;
  deploymentName: string;
  tfDir: string;
  tfVarsFile?: string;
}

/**
 * Infrastructure Manager APIを使用してTerraformデプロイメントを作成・適用
 */
async function deployWithInfrastructureManager(
  config: DeploymentConfig
): Promise<void> {
  const client = new ConfigServiceClient();

  // プロジェクトのロケーション取得
  const parent = client.locationPath(config.projectId, config.location);

  console.log(`Deploying to: ${parent}`);
  console.log(`Deployment Name: ${config.deploymentName}`);

  // Terraformファイルを読み込む
  const tfFiles = readTerraformFiles(config.tfDir);

  // terraform.tfvarsがあれば読み込む
  let tfVars = "";
  if (config.tfVarsFile && fs.existsSync(config.tfVarsFile)) {
    tfVars = fs.readFileSync(config.tfVarsFile, "utf-8");
    console.log("✓ terraform.tfvarsを読み込みました");
  }

  // デプロイメント設定を構築
  const deploymentRequest = {
    parent: parent,
    deploymentId: config.deploymentName,
    deployment: {
      terraformBlueprint: {
        gitSource: {
          repo: buildGitRepo(config.tfDir),
          directory: "",
        },
      },
      labels: {
        environment: "production",
        managed_by: "terraform",
      },
    },
  };

  try {
    console.log("\n📝 デプロイメントを作成中...");
    const [operation] = await client.createDeployment(deploymentRequest);

    console.log(
      `✓ デプロイメント作成リクエストが送信されました: ${operation.name}`
    );

    // オペレーション完了を待機
    const [deployment] = await operation.promise();
    console.log(`✓ デプロイメントが作成されました: ${deployment.name}`);

    // デプロイメントを適用
    await applyDeployment(client, deployment.name);
  } catch (error) {
    console.error("❌ デプロイメント作成エラー:", error);
    throw error;
  }
}

/**
 * デプロイメントを適用（リソースを作成）
 */
async function applyDeployment(
  client: ConfigServiceClient,
  deploymentName: string
): Promise<void> {
  try {
    console.log("\n🚀 デプロイメントを適用中...");

    const request = {
      name: deploymentName,
    };

    const [operation] = await client.applyDeployment(request);
    console.log(`✓ 適用リクエストが送信されました: ${operation.name}`);

    // 適用完了を待機
    const [deployment] = await operation.promise();
    console.log(`✓ デプロイメントが適用されました`);
    console.log(`  状態: ${deployment.state}`);
    console.log(`  ワーカープール: ${deployment.workerPool || "デフォルト"}`);
  } catch (error) {
    console.error("❌ デプロイメント適用エラー:", error);
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
  const client = new ConfigServiceClient();

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
 * Terraformファイルを読み込む
 */
function readTerraformFiles(tfDir: string): Map<string, string> {
  const files = new Map<string, string>();

  if (!fs.existsSync(tfDir)) {
    throw new Error(`ディレクトリが見つかりません: ${tfDir}`);
  }

  const tfFiles = fs
    .readdirSync(tfDir)
    .filter((file) => file.endsWith(".tf"));

  console.log(`\n📂 Terraformファイルを読み込み中...`);
  tfFiles.forEach((file) => {
    const filePath = path.join(tfDir, file);
    const content = fs.readFileSync(filePath, "utf-8");
    files.set(file, content);
    console.log(`  ✓ ${file}`);
  });

  return files;
}

/**
 * Gitリポジトリ情報を構築
 */
function buildGitRepo(tfDir: string): {
  repo: string;
  branch?: string;
  commitSha?: string;
} {
  // 実装パターン1: ローカルパスをGitリポジトリに変換
  // 実装パターン2: GitHub URLを直接指定

  // 例: GitHub URLを返す場合
  return {
    repo: "https://github.com/your-org/your-repo",
    branch: "main",
  };
}

/**
 * デプロイメントを削除
 */
async function destroyDeployment(
  projectId: string,
  location: string,
  deploymentName: string
): Promise<void> {
  const client = new ConfigServiceClient();

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
  // 環境変数またはコマンドライン引数から設定を読み込む
  const projectId = process.env.GCP_PROJECT_ID || "your-project-id";
  const location = process.env.GCP_LOCATION || "us-central1";
  const deploymentName =
    process.env.DEPLOYMENT_NAME || "gcp-billing-alert-deployment";
  const tfDir = process.env.TF_DIR || path.join(__dirname);
  const tfVarsFile =
    process.env.TF_VARS_FILE || path.join(tfDir, "terraform.tfvars");

  const config: DeploymentConfig = {
    projectId,
    location,
    deploymentName,
    tfDir,
    tfVarsFile,
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
