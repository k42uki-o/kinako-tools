# FxTwitter

- `custom.fxtwitter` connects Muse to FxTwitter, a public API that returns X (Twitter) post and profile data as JSON. It needs no login and no credential, and it only reads public data.

- The helper lives at `~/workspace/custom-connectors/custom.fxtwitter/bin/fxtwitter.py`. It calls `https://api.fxtwitter.com` and prints a compact JSON summary.

## Connect

- There is nothing to connect. The API is public, so no credential was registered and no setup link is needed.

- Before the first use in a conversation, prove access with a harmless read:

```text
python3 ~/workspace/custom-connectors/custom.fxtwitter/bin/fxtwitter.py user take_ai_mkt
```

## Credentials

- This connector holds no credential. Never add a key, token, password or cookie to the helper or this doc.

- If FxTwitter ever starts requiring authentication, stop and set the connector up again through the secure credential flow instead of passing a secret in chat.

## Read a post

- Read one public post by its X URL or status ID. Use this when the user shares an X link or asks what a post says.

```text
python3 ~/workspace/custom-connectors/custom.fxtwitter/bin/fxtwitter.py tweet "https://x.com/<user>/status/<id>"
```

- A bare numeric status ID also works. Add `--user <screen_name>` when the ID came without its author.

- The output carries the author name and handle, the post date, the full text, like and repost and reply and view counts, and photo and video URLs. A quoted post is included with its author and text when the API returns one.

- Long-form article posts come back with an article title and metadata only. Read the article body through the live browser when the user needs the full text.

## Read a profile

- Read one public profile by handle. Use this to check who an account is before summarizing its posts.

```text
python3 ~/workspace/custom-connectors/custom.fxtwitter/bin/fxtwitter.py user <screen_name>
```

- The output carries the display name, bio, follower and following counts, total posts and the join date when the API returns it.

## Recover from errors

- An HTTP 404 means the post or account does not exist, was deleted, or is not public. Report that instead of retrying.

- A timeout or a 5xx from the API is safe to retry once. If it fails again, fall back to reading the post through the live browser.

- Engagement counts can lag or differ slightly from what the X app shows. Treat them as approximate.

## Limits

- The connector reads single posts and single profiles only. It cannot read a home timeline, search X, or list an account's posts.

- It cannot post, like, repost or follow. Acting on X is out of scope for this connector.

- Private or login-walled posts are unreachable. Use the live browser for those and say plainly when even that fails.

## Related skills

- Use `muse.skill_search` to find other skills and `muse.connector_search` to find other connectors.
