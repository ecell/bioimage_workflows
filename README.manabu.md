generation

- input
  - parameter
    - seed
    - interval
    - num_samples
    - num_frames
    - exposure_time
  - file
    - なし
- output
  - parameter
    - なし
  - file
    - artifactsのディレクトリ
      - 複数ファイル
        - config.yamlを含む
      - 現状最後に、rmされているので、このあたりほかのものとまぜるときは注意。

analysis1

- input
  - parameter
    - generation
    - min_sigma
    - max_sigma
    - threshold
    - overlap
  - file
    - generation_artifacts = pathlib.Path(client.download_artifacts(generation, "."))
      - generationで渡されたidのrunのartifactを持ってきている。
      - この部分はラッパーで解決してあげたほうが良いだろう。
  - 備考、
- output
  - parameter
    - num_spots
  - file
    - artifactsのディレクトリ
      - 複数ファイル
      - 現状最後に、rmされているので、このあたりほかのものとまぜるときは注意。

analysis2

- input
  - parameter
    - generation
    - analysis1
    - seed
    - max_distance
  - file
    - generation_artifacts = pathlib.Path(client.download_artifacts(generation, "."))
      - generationで渡されたidのrunのartifactを持ってきている。
    - analysis1_artifacts = pathlib.Path(client.download_artifacts(analysis1, "."))
      - analysis1で渡されたidのrunのartifactを持ってきている。
- output
  - paramter
    - なし
  - file
    - artifactsのディレクトリ
      - 単独ファイル
        - histogram2.png
      - 現状最後に、rmされているので、このあたりほかのものとまぜるときは注意。

evaluation

- input
  - parameter
    - generation
    - analysis1
    - max_distance
  - file
    - generation_artifacts = pathlib.Path(client.download_artifacts(generation, "."))
      - generationで渡されたidのrunのartifactを持ってきている。
    - analysis1_artifacts = pathlib.Path(client.download_artifacts(analysis1, "."))
      - analysis1で渡されたidのrunのartifactを持ってきている。
- output
  - parameter
  　　- x_mean
  　　- y_mean
  　　- x_std
  　　- y_std
  　　- r
  　　- miss_count
  　　- missing
  - file
  　　- なし
  　　  - ただしコメントアウトされたコードに heatmap1.png という記述はある。