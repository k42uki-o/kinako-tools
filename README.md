# kinako-tools

きなこ（Muse）の道具一式のバックアップ。2026-11-19 時点のスナップショット。

## 入っているもの

### steam-watch/
Steamセール見張りスクリプト。Steamストアの公開API（cc=jp、キー不要）を使う。
- `check.py` — `games.json` の見張り対象が条件（割引率など）に合えば通知文を出す
- `discover.py` — セール中から「30%以上オフ・好評90%以上・レビュー1,000件以上」を掘り出し物として抽出。`reported.json` で21日間は重複報告を防ぐ
- 運用: 毎週金曜 13:29 JST に実行し、専用チャットへ報告。購入は自動ではしない

### fxtwitter/
FxTwitter（api.fxtwitter.com、認証不要の公開API）でXの単一ポストとプロフィールを読むための道具。
- `bin/fxtwitter.py` — `tweet <url|id>` / `user <handle>`
- `connector.yaml` / `CONNECTOR.md` — カスタムコネクタの定義と説明
- タイムライン・検索・投稿は不可。長文記事はタイトルとメタ情報のみ

## バイナリ等でこのリポジトリに入っていないもの（復元メモ）

- **yt-dlp** v2026.10.26 — 公式GitHub（yt-dlp/yt-dlp）のリリースから単体バイナリを再取得する
- **Irodori-TTS** — 本体は Aratako/Irodori-TTS を再クローンし `uv sync --extra cpu`。モデルは Hugging Face から自動取得。参照音声などの詳細は手元の TOOLS.md に記録
- **Grok Build CLI** v1.0.89 — 公式インストーラ `curl -fsSL https://x.ai/cli/install.sh | bash` で再導入し、本人の SuperGrok アカウントでログインする
