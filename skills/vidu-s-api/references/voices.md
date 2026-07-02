# Vidu-S Live API — System Voices

Pass one of these ids as `avatar.voice` when creating a session. Default is `Tina`.
These are **system** voices — `GET /live/v1/voices` does NOT return them (it only
lists your custom clones). To add a custom voice, use `POST /live/v1/voices/clone`.

## Language support

Every system voice supports the same broad set: **English, French, German, Russian,
Italian, Spanish, Portuguese, Japanese, Korean, Thai, Indonesian, Arabic, Vietnamese,
Turkish, Finnish, Polish, Hindi, Dutch, Czech, Urdu, Tagalog, Swedish, Danish, Hebrew,
Icelandic, Malay, Norwegian, Persian** — plus a Chinese variant. The Chinese variant is
what differs per voice (Mandarin unless noted below), so only that is listed in the table.

## Voice table

| voice id | name | Chinese variant | character |
|---|---|---|---|
| Tina | 甜甜 Tina | Mandarin | warm like milk tea, sweet but sharp (default) |
| Cindy | 林欣宜 Cindy | Taiwan accent | soft, coquettish Taiwan girl |
| Liora Mira | 清欢 Liora Mira | Mandarin | gentle, everyday warmth |
| Sunnybobi | 知芝 Sunnybobi | Mandarin | easygoing, shy girl-next-door |
| Raymond | 林川野 Raymond | Mandarin | clear voice, takeout-loving homebody |
| Ethan | 晨煦 Ethan | Mandarin (northern) | sunny, warm, energetic |
| Theo Calm | 予安 Theo Calm | Mandarin | healing, understanding |
| Serena | 苏瑶 Serena | Mandarin | gentle |
| Harvey | 厚 Harvey | Mandarin | low, mellow, coffee-and-old-books |
| Maia | 四月 Maia | Mandarin | intellectual and gentle |
| Evan | 江晨 Evan | Mandarin | male college student, younger puppy-type |
| Qiao | 小乔妹 Qiao | Taiwan accent | sweet-looking but feisty |
| Momo | 茉兔 Momo | Mandarin | playful, teasing, cheerful |
| Wil | 伟伦 Wil | Mandarin | Shenzhen-raised HK/TW accent |
| Angel | 台普-安琪 Angel | Mandarin | light Taiwan accent, very sweet |
| Li Cassian | 东厂-李公公 Li Cassian | Mandarin | measured, observant |
| Mia | 温柔生活博主-舒然 Mia | Mandarin | delicate, slow-living, healing |
| Joyner | 喜剧担当-阿逗 Joyner | Mandarin | funny, exaggerated, down-to-earth |
| Gold | 金爷 Gold | Mandarin | West Coast Black rapper |
| Katerina | 卡捷琳娜 Katerina | Mandarin | mature "御姐" tone, rhythmic |
| Ryan | 甜茶 Ryan | Mandarin | full rhythm, dramatic tension |
| Jennifer | 詹妮弗 Jennifer | Mandarin | brand-grade cinematic American female |
| Aiden | 艾登 Aiden | Mandarin | American boy, good at cooking |
| Mione | 敏儿 Mione | Mandarin | mature, intellectual British girl-next-door |
| Sunny | 四川-晴儿 Sunny | Sichuan dialect | sweet Sichuan girl |
| Dylan | 北京-晓东 Dylan | Beijing dialect | boy from a Beijing hutong |
| Eric | 四川-程川 Eric | Sichuan dialect | lively Chengdu man |
| Peter | 天津-李彼得 Peter | Tianjin dialect | Tianjin crosstalk, pro straight-man |
| Joseph Chen | 阿樸伯 Joseph Chen | Minnan dialect | old overseas-Chinese from Nanyang |
| Marcus | 陕西-秦川 Marcus | Shaanxi dialect | broad-faced, few words, Shaanxi flavor |
| Li | 南京-老李 Li | Nanjing dialect | grumbling uncle |
| Kiki | 粤语-阿清 Kiki | Cantonese | sweet HK girl bestie |
| Rocky | 粤语-阿强 Rocky | Guangdong/Cantonese | humorous chat companion |
| Sohee | 素熙 Sohee | Mandarin | gentle, cheerful, expressive Korean unnie |
| Lenn | 莱恩 Lenn | Mandarin | rational German youth, rebellious in detail |
| Ono Anna | 小野杏 Ono Anna | Mandarin | mischievous childhood friend |
| Sonrisa | 索尼莎 Sonrisa | Mandarin | warm, cheerful Latina |
| Bodega | 博德加 Bodega | Mandarin | warm Spanish uncle |
| Emilien | 埃米尔安 Emilien | Mandarin | romantic French big-brother |
| Andre | 安德雷 Andre | Mandarin | magnetic, steady male |
| Radio Gol | 拉迪奥·戈尔 Radio Gol | Mandarin | football poet / commentator |
| Alek | 阿列克 Alek | Mandarin | cold-yet-warm Russian |
| Rizky | 阿力 Rizky | Mandarin | Indonesian young man, distinctive |
| Roya | 萝雅 Roya | Mandarin | sporty girl, free spirit |
| Arda | 阿尔达 Arda | Mandarin | clean, gentle, temperate |
| Hana | 阿幸 Hana | Mandarin | dog-loving mature Vietnamese sister |
| Dolce | 多尔切 Dolce | Mandarin | laid-back Italian uncle |
| Jakub | 雅克 Jakub | Mandarin | Polish small-town artsy youth, magnetic |
| Griet | 海娜 Griet | Mandarin | mature, artsy Dutch woman |
| Eliška | 艾莉卡 Eliška | Mandarin | Central-European craft and warmth |
| Marina | 玛丽娜 Marina | Mandarin | girl raised in a multicultural city |
| Siiri | 西芮 Siiri | Mandarin | reserved, gentle, slow like a calm lake |
| Ingrid | 林恩 Ingrid | Mandarin | Norwegian country girl |
| Sigga | 海娜 Sigga | Mandarin | intellectual Icelandic small-town woman |
| Bea | 雅娜 Bea | Mandarin | coffee-loving sweet Filipina |
| Chloe | 思怡 Chloe | Mandarin | Malaysian white-collar woman |
