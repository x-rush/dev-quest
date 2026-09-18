# Merged verification evidence

Merged 4401 current manifest records. Evidence is reused only when `file`, `lang`, and `sha256(manifest.content UTF-8)` match; later run directories take priority. Unmatched content remains `NOT_VERIFIED`. The legacy hash marker is retained but does not override actual L1/L2 evidence. If a manifest has duplicate blocks with the same content key, each may reuse the same matching evidence row.
