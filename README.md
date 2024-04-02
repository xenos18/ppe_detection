# Detection of Pharmaceutical Personal Protective Equipment in Video Stream
***
This repository contains source code of training and inferencing model for PPE detection.

**Abstract**: Pharmaceutical manufacturing is a complex process, where each stage requires a high level of safety and sterility. Personal Protective Equipment (PPE) is used for this purpose. Despite all the measures of control, human factor (improper PPE wearing) causes numerous losses for human health and material property. This research proposes solid computer vision system for ensuring safety in pharmaceutical laboratories. For this we have tested wide range of state-of-the-art object detection methods. Composing previously obtained results in this sphere with our own approach to this problem, we have reached the high accuracy (mAP@0.5) ranging from 0.77 up to 0.98 in detecting all the elements of common set of PPE used in pharmaceutical laboratories. Our system is the step towards safe medicine producing.

**Authors**: Michael Leontiev, Danil Zhilikov, Dmitry Lobanov, Lenar Klimov, Vyacheslav Chertan, Daniel Bobrov, Vladislav Maslov, Vasilii Vologdin, and Ksenia Balabaeva

## Requirements
### Setup Directions
1. Create .env file by copying `.env.example`
2. Insert telegram bot token at `app/bot .env`
3. Insert login/password to RTSP-stream in `app/.env`
4. `docker-compose up --build`

After setups service will be available at [127.0.0.1:8500](url)

## Research notebooks

In folder `/notebooks/` you can access to research notebooks. All notebooks was running on Google Colab.

## Data access

Dataset can be accessed by [link](https://drive.google.com/file/d/13TvqLqCHwDNVK2kBZyHhVPQ80LZ_oA2s/view)

## Help
***
You can contact with us by email (michlea@yandex.ru Michael Leontiev, kyubalabaeva@gmail.com Ksenia Balabaeva) or Telegram (@michlea_tg Michael Leontiev) and ask your questions.

## License
***
Our service is open-sourced software licensed under the MIT license.