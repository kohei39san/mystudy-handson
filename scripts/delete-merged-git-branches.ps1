# マージ済みブランチを一括削除
git branch --merged | Where-Object { $_ -notmatch "\*|main|master" } | ForEach-Object { git branch -d $_.Trim() }