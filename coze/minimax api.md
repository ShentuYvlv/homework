# 异步长文本语音生成（T2A Async）

> 该 API 支持基于文本到语音的异步生成，单次文本生成传输最大支持 100 万字符，生成的完整音频结果支持异步的方式进行检索。

该接口支持以下功能：

1. 支持 100+系统音色、复刻音色自主选择；
2. 支持语调、语速、音量、比特率、采样率、输出格式自主调整；
3. 支持音频时长、音频大小等返回参数；
4. 支持时间戳（字幕）返回，精确到句；
5. 支持直接传入字符串与上传文本文件 file\_id 两种方式进行待合成文本的输入；
6. 支持非法字符检测：非法字符不超过 10%（包含 10%），音频会正常生成并返回非法字符占比；非法字符超过 10%，接口不返回结果（返回报错码），请检测后再次进行请求【非法字符定义：ascii 码中的控制符（不含制表符和换行符）】。

提交长文本语音合成请求后，会生成 file\_id，生成任务完成后，可通过 file\_id 使用文件检索接口进行下载。

⚠️ 注意：返回的 url 的有效期为：自 url 返回开始的**9 个小时**（即 32400 秒），超过有效期后 url 便会失效，生成的信息便会丢失，请注意下载信息的时间。

**适用场景：整本书籍等长文本的语音生成。**

## 支持模型

以下为 MiniMax 提供的语音模型及其特性说明。

| 模型               | 特性                                 |
| :--------------- | :--------------------------------- |
| speech-2.6-hd    | 最新的 HD 模型，韵律表现出色，极致音质与韵律表现，生成更快更自然 |
| speech-2.6-turbo | 最新的 Turbo 模型，音质优异，超低时延，响应更灵敏       |
| speech-02-hd     | 拥有出色的韵律、稳定性和复刻相似度，音质表现突出           |
| speech-02-turbo  | 拥有出色的韵律和稳定性，小语种能力加强，性能表现出色         |

## 接口说明

整体包含 2 个 API：创建**语音生成任务**、**查询语音生成任务状态**。使用步骤如下：

1. 创建语音生成任务得到 task\_id（如果选择以 file\_id 的形式传入待合成文本，需要前置使用 File(Upload)接口进行文件上传）；
2. 基于 taskid 查询语音生成任务状态；
3. 如果发现任务生成成功，那么可以使用本接口返回的 file\_id 通过 File API 进行结果查看和下载。

## 支持语言

MiniMax 的语音合成模型具备卓越的跨语言能力，全面支持 40 种全球广泛使用的语言。我们致力于打破语言壁垒，构建真正意义上的全球通用人工智能模型。

目前支持的语言包含：

| 支持语种                |                      |                       |
| :------------------ | :------------------- | :-------------------- |
| 1. 中文（Chinese）      | 15. 土耳其语（Turkish）    | 28. 马来语（Malay）        |
| 2. 粤语（Cantonese）    | 16. 荷兰语（Dutch）       | 29. 波斯语（Persian）      |
| 3. 英语（English）      | 17. 乌克兰语（Ukrainian）  | 30. 斯洛伐克语（Slovak）     |
| 4. 西班牙语（Spanish）    | 18. 泰语（Thai）         | 31. 瑞典语（Swedish）      |
| 5. 法语（French）       | 19. 波兰语（Polish）      | 32. 克罗地亚语（Croatian）   |
| 6. 俄语（Russian）      | 20. 罗马尼亚语（Romanian）  | 33. 菲律宾语（Filipino）    |
| 7. 德语（German）       | 21. 希腊语（Greek）       | 34. 匈牙利语（Hungarian）   |
| 8. 葡萄牙语（Portuguese） | 22. 捷克语（Czech）       | 35. 挪威语（Norwegian）    |
| 9. 阿拉伯语（Arabic）     | 23. 芬兰语（Finnish）     | 36. 斯洛文尼亚语（Slovenian） |
| 10. 意大利语（Italian）   | 24. 印地语（Hindi）       | 37. 加泰罗尼亚语（Catalan）   |
| 11. 日语（Japanese）    | 25. 保加利亚语（Bulgarian） | 38. 尼诺斯克语（Nynorsk）    |
| 12. 韩语（Korean）      | 26. 丹麦语（Danish）      | 39. 泰米尔语（Tamil）       |
| 13. 印尼语（Indonesian） | 27. 希伯来语（Hebrew）     | 40. 阿非利卡语（Afrikaans）  |
| 14. 越南语（Vietnamese） |                      |                       |

## 官方 MCP

MiniMax 提供官方的 [Python 版本](https://github.com/MiniMax-AI/MiniMax-MCP) 和 [JavaScript 版本](https://github.com/MiniMax-AI/MiniMax-MCP-JS) 模型上下文协议（MCP）服务器实现代码，支持语音合成功能，详细说明请参考 [MiniMax MCP 使用指南](/guides/mcp-guide)


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://platform.minimaxi.com/docs/llms.txt

# 创建异步语音合成任务

> 使用本接口，创建异步语音合成任务。

## OpenAPI

````yaml api-reference/speech/t2a-async/api/openapi.json post /v1/t2a_async_v2
openapi: 3.1.0
info:
  title: MiniMax T2A Async API
  description: >-
    MiniMax Text-to-Audio Async API with support for long text processing and
    task querying
  license:
    name: MIT
  version: 1.0.0
servers:
  - url: https://api.minimaxi.com
security:
  - bearerAuth: []
paths:
  /v1/t2a_async_v2:
    post:
      tags:
        - Text to Audio
      summary: Text to Audio Async V2
      operationId: t2aAsyncV2
      parameters:
        - name: Content-Type
          in: header
          required: true
          description: 请求体的媒介类型，请设置为 `application/json`，确保请求数据的格式为 JSON
          schema:
            type: string
            enum:
              - application/json
            default: application/json
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/T2AAsyncV2Req'
            examples:
              文本输入:
                value:
                  model: speech-2.6-hd
                  text: 真正的危险不是计算机开始像人一样思考，而是人开始像计算机一样思考。计算机只是可以帮我们处理一些简单事务。
                  language_boost: auto
                  voice_setting:
                    voice_id: audiobook_male_1
                    speed: 1
                    vol: 1
                    pitch: 1
                  pronunciation_dict:
                    tone:
                      - 危险/dangerous
                  audio_setting:
                    audio_sample_rate: 32000
                    bitrate: 128000
                    format: mp3
                    channel: 2
                  voice_modify:
                    pitch: 0
                    intensity: 0
                    timbre: 0
                    sound_effects: spacious_echo
              文件输入:
                value:
                  model: speech-2.6-hd
                  text_file_id: text_file_id
                  language_boost: auto
                  voice_setting:
                    voice_id: audiobook_male_1
                    speed: 1
                    vol: 10
                    pitch: 1
                  pronunciation_dict:
                    tone:
                      - 草地/(cao3)(di1)
                  audio_setting:
                    audio_sample_rate: 32000
                    bitrate: 128000
                    format: mp3
                    channel: 2
                  voice_modify:
                    pitch: 0
                    intensity: 0
                    timbre: 0
                    sound_effects: spacious_echo
        required: true
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/T2AAsyncV2Resp'
              examples:
                文本输入:
                  value:
                    task_id: 95157322514444
                    task_token: eyJhbGciOiJSUz
                    file_id: 95157322514444
                    usage_characters: 101
                    base_resp:
                      status_code: 0
                      status_msg: success
                文件输入:
                  value:
                    task_id: 95157322514444
                    task_token: eyJhbGciOiJSUz
                    file_id: 95157322514444
                    usage_characters: 101
                    base_resp:
                      status_code: 0
                      status_msg: success
components:
  schemas:
    T2AAsyncV2Req:
      type: object
      required:
        - model
        - text
        - text_file_id
        - voice_setting
      properties:
        model:
          type: string
          description: >-
            请求的模型版本，可选范围：`speech-2.6-hd`, `speech-2.6-turbo`, `speech-02-hd`,
            `speech-02-turbo`, `speech-01-hd`, `speech-01-turbo`.
          enum:
            - speech-2.6-hd
            - speech-2.6-turbo
            - speech-02-hd
            - speech-02-turbo
            - speech-01-hd
            - speech-01-turbo
        text:
          type: string
          description: 待合成音频的文本，限制最长 5 万字符。和 `text_file_id` 二选一必填
        text_file_id:
          type: integer
          format: int64
          description: "待合成音频的文本文件 待合成音频的文本文件 id，单个文件长度限制小于 10 万字符，支持的文件格式：txt、zip。和 `text` 二选一必填，传入后自动校验格式。\n- **txt 文件**：长度限制 <100,000 字符。支持使用 <#x#> 标记自定义停顿。x 为停顿时长（单位：秒），范围 [0.01,99.99]，最多保留两位小数。注意停顿需设置在两个可以语音发音的文本之间，不可连续使用多个停顿标记\n- **zip 文件**：\n\t- 压缩包内需包含同一格式的 txt 或 json 文件。\n\t- json 文件格式：支持 [`title`, `content`, `extra`] 三个字段，分别表示标题、正文、附加信息。若三个字段都存在，则产出 3 组结果，共 9 个文件，统一存放在一个文件夹中。若某字段不存在或内容为空，则该字段不会生成对应结果"
        voice_setting:
          $ref: '#/components/schemas/T2AAsyncV2VoiceSetting'
        audio_setting:
          $ref: '#/components/schemas/T2AAsyncV2AudioSetting'
        pronunciation_dict:
          $ref: '#/components/schemas/T2AAsyncV2PronunciationDict'
        language_boost:
          type: string
          description: 是否增强对指定的小语种和方言的识别能力。默认值为 `null`，可设置为 `auto` 让模型自主判断。
          enum:
            - Chinese
            - Chinese,Yue
            - English
            - Arabic
            - Russian
            - Spanish
            - French
            - Portuguese
            - German
            - Turkish
            - Dutch
            - Ukrainian
            - Vietnamese
            - Indonesian
            - Japanese
            - Italian
            - Korean
            - Thai
            - Polish
            - Romanian
            - Greek
            - Czech
            - Finnish
            - Hindi
            - Bulgarian
            - Danish
            - Hebrew
            - Malay
            - Persian
            - Slovak
            - Swedish
            - Croatian
            - Filipino
            - Hungarian
            - Norwegian
            - Slovenian
            - Catalan
            - Nynorsk
            - Tamil
            - Afrikaans
            - auto
          default: null
        voice_modify:
          $ref: '#/components/schemas/VoiceModify'
        aigc_watermark:
          type: boolean
          description: 控制在合成音频的末尾添加音频节奏标识，默认值为 False。该参数仅对非流式合成生效
          default: false
    T2AAsyncV2Resp:
      type: object
      properties:
        task_id:
          type: string
          description: 当前任务的 ID
        file_id:
          type: integer
          format: int64
          description: >-
            任务创建成功后返回的对应音频文件的 ID。

            - 当任务完成后，可通过 file_id 调用
            [文件检索接口](/api-reference/file-management-retrieve) 进行下载

            - 当请求出错时，不返回该字段

            注意：返回的下载 URL 自生成起 9 小时（32,400 秒）内有效，过期后文件将失效，生成的信息便会丢失，请注意下载信息的时间
        task_token:
          type: string
          description: 完成当前任务使用的密钥信息
        usage_characters:
          type: integer
          description: 计费字符数
        base_resp:
          $ref: '#/components/schemas/BaseResp'
    T2AAsyncV2VoiceSetting:
      type: object
      required:
        - voice_id
      properties:
        voice_id:
          type: string
          description: "合成音频的音色编号。若需要设置混合音色，请设置 timbre_weights 参数，本参数设置为空值。支持系统音色、复刻音色以及文生音色三种类型，以下是部分最新的系统音色（ID），可查看 [系统音色列表](/faq/system-voice-id) 或使用 [查询可用音色 API](/api-reference/voice-management-get) 查询系统支持的全部音色\n\n - **中文**:\n\t- moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85\n\t- moss_audio_aaa1346a-7ce7-11f0-8e61-2e6e3c7ee85d\n\t- Chinese (Mandarin)_Lyrical_Voice\n\t- Chinese (Mandarin)_HK_Flight_Attendant\n- **英文**:\n\t- English_Graceful_Lady\n\t- English_Insightful_Speaker\n\t- English_radiant_girl\n\t- English_Persuasive_Man\n\t- moss_audio_6dc281eb-713c-11f0-a447-9613c873494c\n\t- moss_audio_570551b1-735c-11f0-b236-0adeeecad052\n\t- moss_audio_ad5baf92-735f-11f0-8263-fe5a2fe98ec8\n\t- English_Lucky_Robot\n- **日文**:\n\t- Japanese_Whisper_Belle\n\t- moss_audio_24875c4a-7be4-11f0-9359-4e72c55db738\n\t- moss_audio_7f4ee608-78ea-11f0-bb73-1e2a4cfcd245\n\t- moss_audio_c1a6a3ac-7be6-11f0-8e8e-36b92fbb4f95"
        speed:
          type: number
          format: float
          description: 合成音频的语速，取值越大，语速越快。取值范围 `[0.5,2]`，默认值为1.0
          minimum: 0.5
          maximum: 2
          default: 1
        vol:
          type: number
          format: float
          description: 合成音频的音量，取值越大，音量越高。取值范围 `(0,10]`，默认值为 1.0
          exclusiveMinimum: 0
          maximum: 10
          default: 1
        pitch:
          type: integer
          description: 合成音频的语调，取值范围 `[-12,12]`，默认值为 0，其中 0 为原音色输出
          minimum: -12
          maximum: 12
          default: 0
        emotion:
          type: string
          description: "控制合成语音的情绪，参数范围 `[\"happy\", \"sad\", \"angry\", \"fearful\", \"disgusted\", \"surprised\", \"calm\", \"fluent\", \"whipser\"]`，分别对应 8 种情绪：高兴，悲伤，愤怒，害怕，厌恶，惊讶，中性，生动，低语 \r\n- 模型会根据输入文本自动匹配合适的情绪，一般无需手动指定  \r\n- 该参数仅对 `speech-2.6-hd`, `speech-2.6-turbo`, `speech-02-hd`, `speech-02-turbo`, `speech-01-hd`, `speech-01-turbo` 模型生效 \r\n- 选项 `fluent`, `whisper` 仅对 `speech-2.6-turbo`, `speech-2.6-hd` 模型生效"
          enum:
            - happy
            - sad
            - angry
            - fearful
            - disgusted
            - surprised
            - calm
            - fluent
            - whisper
        english_normalization:
          type: boolean
          description: 支持英语文本规范化，开启后可提升数字阅读场景的性能，但会略微增加延迟，默认 false
          default: false
    T2AAsyncV2AudioSetting:
      type: object
      properties:
        audio_sample_rate:
          type: integer
          format: int64
          default: 32000
          description: 生成音频的采样率。可选范围 `[8000，16000，22050，24000，32000，44100]`，默认为 `32000`
        bitrate:
          type: integer
          format: int64
          default: 128000
          description: >-
            生成音频的比特率。可选范围 `[32000，64000，128000，256000]`，默认值为 `128000`。该参数仅对
            `mp3` 格式的音频生效
        format:
          type: string
          description: 生成音频的格式。可选范围`[mp3, pcm, flac]`，默认值为 `mp3`
          enum:
            - mp3
            - pcm
            - flac
          default: mp3
        channel:
          type: integer
          format: int64
          default: 2
          description: 生成音频的声道数。可选范围：`[1,2]`，其中 `1` 为单声道，`2` 为双声道，默认值为 1
    T2AAsyncV2PronunciationDict:
      type: object
      properties:
        tone:
          type: array
          description: |-
            定义需要特殊标注的文字或符号对应的注音或发音替换规则。在中文文本中，声调用数字表示：
            一声为 1，二声为 2，三声为 3，四声为 4，轻声为 5
            示例如下：
            `["燕少飞/(yan4)(shao3)(fei1)", "omg/oh my god"]`
          items:
            type: string
    VoiceModify:
      type: object
      description: 声音效果器设置
      properties:
        pitch:
          type: integer
          description: >-
            音高调整（低沉/明亮），范围 [-100,100]，数值接近 -100，声音更低沉；接近 100，声音更明亮


            ![pitch
            adjustment](https://filecdn.minimax.chat/public/5d210c47-4236-4e81-893b-16cc1ef0302d.png)
          minimum: -100
          maximum: 100
        intensity:
          type: integer
          description: >-
            强度调整（力量感/柔和），范围 [-100,100]，数值接近 -100，声音更刚劲；接近 100，声音更轻柔


            ![intensity
            adjustment](https://filecdn.minimax.chat/public/862d493e-71d5-4d1f-b7c3-9ac51890631b.png)
          minimum: -100
          maximum: 100
        timbre:
          type: integer
          description: >-
            音色调整（磁性/清脆），范围 [-100,100]，数值接近 -100，声音更浑厚；数值接近 100，声音更清脆


            ![timbre
            adjustment](https://filecdn.minimax.chat/public/5f0e6cae-363a-452b-8d42-fbc4ef5a0510.png)
          minimum: -100
          maximum: 100
        sound_effects:
          type: string
          description: |-
            音效设置，单次仅能选择一种，可选值：
            1. spacious_echo（空旷回音）
            2. auditorium_echo（礼堂广播）
            3. lofi_telephone（电话失真）
            4. robotic（电音）
          enum:
            - spacious_echo
            - auditorium_echo
            - lofi_telephone
            - robotic
    BaseResp:
      type: object
      description: 本次请求的状态码及其详情
      required:
        - status_code
        - status_msg
      properties:
        status_code:
          type: integer
          format: int64
          description: |-
            状态码

            - `0`: 正常
            - `1002`: 限流
            - `1004`: 鉴权失败
            - `1039`: 触发 TPM 限流
            - `1042`: 非法字符超10%
            - `2013`: 参数错误

            更多内容可查看 [错误码查询列表](/api-reference/errorcode) 了解详情
        status_msg:
          type: string
          description: 状态详情
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |-
        `HTTP: Bearer Auth`
         - Security Scheme Type: http
         - HTTP Authorization Scheme: Bearer API_key，用于验证账户信息，可在 [账户管理>接口密钥](https://platform.minimaxi.com/user-center/basic-information/interface-key) 中查看。

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://platform.minimaxi.com/docs/llms.txt


# 查询语音生成任务状态

> 使用本接口，查询异步语音合成任务状态。

## OpenAPI

````yaml api-reference/speech/t2a-async/api/openapi.json get /v1/query/t2a_async_query_v2
openapi: 3.1.0
info:
  title: MiniMax T2A Async API
  description: >-
    MiniMax Text-to-Audio Async API with support for long text processing and
    task querying
  license:
    name: MIT
  version: 1.0.0
servers:
  - url: https://api.minimaxi.com
security:
  - bearerAuth: []
paths:
  /v1/query/t2a_async_query_v2:
    get:
      tags:
        - Text to Audio
      summary: Query T2A Async V2 Task Status
      operationId: t2aAsyncV2Query
      parameters:
        - name: task_id
          in: query
          required: true
          description: 任务 ID，提交任务时返回的信息
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/T2AAsyncV2QueryResp'
components:
  schemas:
    T2AAsyncV2QueryResp:
      type: object
      properties:
        task_id:
          type: integer
          format: int64
          description: 任务 ID
        status:
          type: string
          description: |-
            该任务的当前状态。

            - **Processing**: 该任务正在处理中
            - **Success**: 该任务已完成
            - **Failed**: 任务失败
            - **Expired**: 任务已过期
          enum:
            - success
            - failed
            - expired
            - processing
        file_id:
          type: integer
          format: int64
          description: >-
            任务创建成功后返回的对应音频文件的 ID。

            - 当任务完成后，可通过 file_id 调用
            [文件检索接口](/api-reference/file-management-retrieve) 进行下载

            - 当请求出错时，不返回该字段

            注意：返回的下载 URL 自生成起 9 小时（32,400 秒）内有效，过期后文件将失效，生成的信息便会丢失，请注意下载信息的时间
        base_resp:
          $ref: '#/components/schemas/BaseResp'
      example:
        task_id: 95157322514444
        status: Processing
        file_id: 95157322514496
        base_resp:
          status_code: 0
          status_msg: success
    BaseResp:
      type: object
      description: 本次请求的状态码及其详情
      required:
        - status_code
        - status_msg
      properties:
        status_code:
          type: integer
          format: int64
          description: |-
            状态码

            - `0`: 正常
            - `1002`: 限流
            - `1004`: 鉴权失败
            - `1039`: 触发 TPM 限流
            - `1042`: 非法字符超10%
            - `2013`: 参数错误

            更多内容可查看 [错误码查询列表](/api-reference/errorcode) 了解详情
        status_msg:
          type: string
          description: 状态详情
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |-
        `HTTP: Bearer Auth`
         - Security Scheme Type: http
         - HTTP Authorization Scheme: Bearer API_key，用于验证账户信息，可在 [账户管理>接口密钥](https://platform.minimaxi.com/user-center/basic-information/interface-key) 中查看。

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://platform.minimaxi.com/docs/llms.txt


# 查询可用音色ID

> 使用本接口支持查询不同分类下的音色信息。

## OpenAPI

````yaml api-reference/speech/voice-management/api/openapi.json post /v1/get_voice
openapi: 3.1.0
info:
  title: MiniMax Voice Management API
  description: MiniMax Voice Management API with support for getting and deleting voices
  license:
    name: MIT
  version: 1.0.0
servers:
  - url: https://api.minimaxi.com
security:
  - bearerAuth: []
paths:
  /v1/get_voice:
    post:
      tags:
        - Voice
      summary: Get Voice
      operationId: getVoice
      parameters:
        - name: Content-Type
          in: header
          required: true
          description: 请求体的媒介类型，请设置为 `application/json`，确保请求数据的格式为 JSON
          schema:
            type: string
            enum:
              - application/json
            default: application/json
      requestBody:
        description: ''
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/GetVoiceReq'
        required: true
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GetVoiceResp'
components:
  schemas:
    GetVoiceReq:
      type: object
      required:
        - voice_type
      properties:
        voice_type:
          type: string
          description: |-
            希望查询音色类型，支持以下取值：

            - `system`: 系统音色
            - `voice_cloning`: 快速复刻的音色，仅在成功用于语音合成后才可查询
            - `voice_generation`: 文生音色接口生成的音色，仅在成功用于语音合成后才可查询
            - `all`: 以上全部
          enum:
            - system
            - voice_cloning
            - voice_generation
            - all
      example:
        voice_type: all
    GetVoiceResp:
      type: object
      properties:
        system_voice:
          type: array
          items:
            $ref: '#/components/schemas/SystemVoiceInfo'
          description: 包含系统预定义的音色。
        voice_cloning:
          type: array
          items:
            $ref: '#/components/schemas/VoiceCloningInfo'
          description: 包含音色快速复刻的音色数据
        voice_generation:
          type: array
          items:
            $ref: '#/components/schemas/VoiceGenerationInfo'
          description: 包含音色生成接口产生的音色数据
        base_resp:
          $ref: '#/components/schemas/BaseResp'
      example:
        system_voice:
          - voice_id: Chinese (Mandarin)_Reliable_Executive
            description:
              - 一位沉稳可靠的中年男性高管声音，标准普通话，传递出值得信赖的感觉。
            voice_name: 沉稳高管
            created_time: '1970-01-01'
          - voice_id: Chinese (Mandarin)_News_Anchor
            description:
              - 一位专业、播音腔的中年女性新闻主播，标准普通话。
            voice_name: 新闻女声
            created_time: '1970-01-01'
        voice_cloning:
          - voice_id: test12345
            description: []
            created_time: '2025-08-20'
          - voice_id: test12346
            description: []
            created_time: '2025-08-21'
        voice_generation:
          - voice_id: ttv-voice-2025082011321125-2uEN0X1S
            description: []
            created_time: '2025-08-20'
          - voice_id: ttv-voice-2025082014225025-ZCQt0U0k
            description: []
            created_time: '2025-08-20'
        base_resp:
          status_code: 0
          status_msg: success
    SystemVoiceInfo:
      type: object
      properties:
        voice_id:
          type: string
          description: 音色 ID
        voice_name:
          type: string
          description: 音色名称，非调用的音色 ID
        description:
          type: array
          items:
            type: string
          description: 音色描述
    VoiceCloningInfo:
      type: object
      properties:
        voice_id:
          type: string
          description: 音色 ID
        description:
          type: array
          items:
            type: string
          description: 生成音色时填写的音色描述
        created_time:
          type: string
          description: 创建时间，格式 yyyy-mm-dd
    VoiceGenerationInfo:
      type: object
      properties:
        voice_id:
          type: string
          description: 音色 ID
        description:
          type: array
          items:
            type: string
          description: 生成音色时填写的音色描述
        created_time:
          type: string
          description: 创建时间，格式 yyyy-mm-dd
    BaseResp:
      type: object
      description: 本次请求的状态码和详情
      properties:
        status_code:
          type: integer
          format: int64
          description: |-
            状态码。

            - `0`: 请求结果正常
            - `2013`: 输入参数信息不正常

            更多内容可查看 [错误码查询列表](/api-reference/errorcode) 了解详情
        status_msg:
          type: string
          description: 状态详情
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |-
        `HTTP: Bearer Auth`
         - Security Scheme Type: http
         - HTTP Authorization Scheme: Bearer API_key，用于验证账户信息，可在 [账户管理>接口密钥](https://platform.minimaxi.com/user-center/basic-information/interface-key) 中查看。

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://platform.minimaxi.com/docs/llms.txt

