$ErrorActionPreference = 'Stop'

function Write-DenyDecision {
    param([string]$Reason)

    [ordered]@{
        permissionDecision = 'deny'
        permissionDecisionReason = $Reason
        hookSpecificOutput = [ordered]@{
            hookEventName = 'PreToolUse'
            permissionDecision = 'deny'
            permissionDecisionReason = $Reason
        }
    } | ConvertTo-Json -Depth 5 -Compress
}

try {
    $inputStream = [Console]::OpenStandardInput()
    $memoryStream = New-Object System.IO.MemoryStream
    $inputStream.CopyTo($memoryStream)
    $eventJson = [System.Text.Encoding]::UTF8.GetString($memoryStream.ToArray())
    $event = $eventJson | ConvertFrom-Json
} catch {
    Write-DenyDecision 'Unable to read the hook event; terminal command was blocked.'
    exit 0
}

$toolName = if ($event.tool_name) { $event.tool_name } else { $event.toolName }
if ($toolName -notin @('run_in_terminal', 'send_to_terminal', 'powershell', 'bash', 'Bash')) {
    exit 0
}

$toolInput = if ($event.tool_input) { $event.tool_input } else { $event.toolArgs }
$commandText = $toolInput.command
if ($commandText -isnot [string] -or [string]::IsNullOrWhiteSpace($commandText)) {
    Write-DenyDecision 'Terminal command input was missing or had an unexpected format.'
    exit 0
}

$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseInput(
    $commandText,
    [ref]$tokens,
    [ref]$parseErrors
)

if ($parseErrors.Count -gt 0) {
    Write-DenyDecision 'PowerShell could not parse the terminal input; submit one valid command at a time.'
    exit 0
}

$commands = $ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.CommandAst] }, $true)
$multipleStatements = $ast.FindAll({
    param($node)
    ($node -is [System.Management.Automation.Language.ScriptBlockAst] -and
        $node.EndBlock -and $node.EndBlock.Statements.Count -gt 1) -or
    ($node -is [System.Management.Automation.Language.StatementBlockAst] -and
        $node.Statements.Count -gt 1)
}, $true).Count -gt 0
$hasPipeline = $ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.PipelineAst] -and
        $node.PipelineElements.Count -gt 1
}, $true).Count -gt 0

if ($commands.Count -gt 1 -or $multipleStatements -or $hasPipeline) {
    Write-DenyDecision 'Only one PowerShell command is allowed per terminal call; command chaining and pipelines are blocked.'
}