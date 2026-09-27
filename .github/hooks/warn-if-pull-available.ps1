$ErrorActionPreference = 'Stop'

function Write-SystemMessage {
    param([string]$Message)

    [ordered]@{
        systemMessage = $Message
        additionalContext = $Message
    } | ConvertTo-Json -Compress
}

try {
    $null = & git fetch --quiet 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-SystemMessage 'git fetch に失敗したため、git pull が必要か確認できませんでした。'
        exit 0
    }

    $status = & git status --porcelain=v2 --branch 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-SystemMessage 'リモートとの差分を確認できませんでした。'
        exit 0
    }

    if (-not ($status | Where-Object { $_ -like '# branch.upstream *' })) {
        exit 0
    }

    $aheadBehind = $status | Where-Object { $_ -match '^# branch\.ab \+\d+ -\d+$' } | Select-Object -First 1
    if ($aheadBehind -match '^# branch\.ab \+(\d+) -(\d+)$') {
        $ahead = [int]$Matches[1]
        $behind = [int]$Matches[2]
    } else {
        Write-SystemMessage 'リモートとの差分を確認できませんでした。'
        exit 0
    }

    if ($behind -gt 0) {
        if ($ahead -gt 0) {
            Write-SystemMessage "upstream に未取得コミットが $behind 件あります。ローカルにも未送信コミットが $ahead 件あるため、git pull の前に差分と merge/rebase 設定を確認してください。"
        } else {
            Write-SystemMessage "upstream に未取得コミットが $behind 件あります。必要であれば git pull で取り込んでください。"
        }
    }
} catch {
    Write-SystemMessage 'git fetch または upstream の確認に失敗したため、git pull が必要か確認できませんでした。'
}