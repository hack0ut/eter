def send_message(text: str, url: str):  # Обычное сообщение
    return f'<script type="text/javascript">alert("{text}");window.location.href = "{url}";</script>'


def send_prompt(text: str, url: str):  # Строка с вводом
    return f'<script type="text/javascript">prompt("{text}");window.location.href = "{url}";</script>'


def send_confirm(text: str, url: str):  # Подтверждение
    return f'<script type="text/javascript">confirm("{text}");window.location.href = "{url}";</script>'
