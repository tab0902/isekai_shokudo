import os
import logging
import traceback
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import FollowEvent, PostbackEvent, MessageEvent, ImageMessage, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction
from main.models import Post

# Create your views here.

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
logger = logging.getLogger(__name__)

@csrf_exempt
def callback(request):
    def startButton(reply_token, send_text):
        try:
            reply = line_bot_api.reply_message(
                reply_token,
                [
                    TextSendMessage(send_text),
                    TemplateSendMessage(
                        alt_text='メニューを更新',
                        template=ButtonsTemplate(
                            title='メニューを更新',
                            text='更新ボタンを押してください',
                            actions=[
                                PostbackTemplateAction(
                                    label='メニューを更新',
                                    data='start'
                                ),
                            ]
                        )
                    )
                ]
            )
        except LineBotApiError:
            return HttpResponseBadRequest()
        return reply

    def confirmButton(reply_token, send_text):
        try:
            reply = line_bot_api.reply_message(
                reply_token,
                [
                    TextSendMessage(send_text),
                    TemplateSendMessage(
                        alt_text='確認',
                        template=ButtonsTemplate(
                            title='確認',
                            text='選択してください',
                            actions=[
                                PostbackTemplateAction(
                                    label='更新',
                                    data='save'
                                ),
                                PostbackTemplateAction(
                                    label='中止',
                                    data='quit'
                                ),
                            ]
                        )
                    )
                ]
            )
        except LineBotApiError:
            return HttpResponseBadRequest()
        return reply

    if request.method == 'POST':
        body = request.body.decode('utf-8')
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            posts = Post.objects.values('user_id').order_by('-created_at')
            users = []
            for post in posts:
                users.append(post['user_id'])
            has_created = event.source.user_id in users
            if has_created == True:
                post = Post.objects.filter(user_id=event.source.user_id).order_by('-created_at')[0]

            if isinstance(event, FollowEvent):
                startButton(
                    event.reply_token,
                    'フォローありがとうございます！\nメニューを更新したい場合、下のボタンを押してください\nなお、以下がサイトのURLです\n\nhttps://{}'.format(settings.DOMAIN_NAME)
                )

            elif isinstance(event, PostbackEvent):
                if event.postback.data == 'start':
                    if has_created == False:
                        post = Post(user_id=event.source.user_id, status=1)
                        post.save()
                        try:
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage('メニューの更新ですね\nまずは料理名を入力してください')
                            )
                        except LineBotApiError:
                            return HttpResponseBadRequest()
                    else:
                        if post.status == 0:
                            post = Post(user_id=event.source.user_id, status=1)
                            post.save()
                            try:
                                line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage('メニューの更新ですね\nまずは料理名を入力してください')
                                )
                            except LineBotApiError:
                                return HttpResponseBadRequest()

                elif event.postback.data == 'save':
                    if has_created == True:
                        if post.status == 5:
                            post.status = 0
                            post.save()
                            try:
                                line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage('サイトが更新されました\n\nhttps://{}'.format(settings.DOMAIN_NAME))
                                )
                            except LineBotApiError:
                                return HttpResponseBadRequest()

                elif event.postback.data == 'quit':
                    if has_created == True:
                        if post.status == 5:
                            post.image_path.delete()
                            post.delete()
                            try:
                                line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage('操作中のデータを削除しました')
                                )
                            except LineBotApiError:
                                return HttpResponseBadRequest()

            elif isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    if event.message.text == 'ニッポンポン':
                        del_posts = Post.objects.exclude(Q(image_path__contains='ebi-fry') | Q(image_path__contains='katsu-don') | Q(image_path__contains='beef-stew'))
                        for del_post in del_posts:
                            del_post.image_path.delete()
                        Post.objects.all().delete()
                        try:
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage('合衆国ニッポンポン！！！')
                            )
                        except LineBotApiError:
                            return HttpResponseBadRequest()
                    elif event.message.text == 'ナナリー':
                        del_posts = Post.objects.exclude(Q(image_path__contains='ebi-fry') | Q(image_path__contains='katsu-don') | Q(image_path__contains='beef-stew'))
                        for del_post in del_posts:
                            del_post.image_path.delete()
                        Post.objects.all().delete()
                        Post.objects.bulk_create([
                            Post(
                                title = 'エビフライ',
                                description = 'プリプリのエビをカリカリの衣で包んだ至高の一品',
                                price = '850',
                                image_path = 'img/post/ebi-fry.jpg',
                                status = 0
                            ),
                            Post(
                                title = 'シチュー',
                                description = 'バラ肉をルーとともにホロホロになるまで煮込んだビーフシチュー',
                                price = '1200',
                                image_path = 'img/post/beef-stew.jpg',
                                status = 0
                            ),
                            Post(
                                title = 'かつ丼',
                                description = '揚げたてのカツをふんわり半熟卵でとじた定番の一品',
                                price = '750',
                                image_path = 'img/post/katsu-don.jpg',
                                status = 0
                            ),
                        ])
                        try:
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage('ナナリーーーーーッッ！！！！！')
                            )
                        except LineBotApiError:
                            return HttpResponseBadRequest()

                    if has_created == True:
                        if post.status == 0:
                            startButton(
                                event.reply_token,
                                'ご利用ありがとうございます\nメニューを更新したい場合、下のボタンを押してください\nなお、以下がサイトのURLです\n\nhttps://{}'.format(settings.DOMAIN_NAME)
                            )
                        elif post.status == 1:
                            post.title = event.message.text
                            post.status = 2
                            post.save()
                            try:
                                line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage('次はメニューの説明文を入力してください'),
                                )
                            except LineBotApiError:
                                return HttpResponseBadRequest()
                        elif post.status == 2:
                            post.description = event.message.text
                            post.status = 3
                            post.save()
                            try:
                                line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage('次は値段を入力してください'),
                                )
                            except LineBotApiError:
                                return HttpResponseBadRequest()
                        elif post.status == 3:
                            try:
                                post.price = int(event.message.text)
                                post.status = 4
                                post.save()
                            except:
                                try:
                                    line_bot_api.reply_message(
                                        event.reply_token,
                                        TextSendMessage('半角数字を入力してください'),
                                    )
                                except LineBotApiError:
                                    return HttpResponseBadRequest()
                            try:
                                line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage('次は掲載する画像を送信してください'),
                                )
                            except LineBotApiError:
                                return HttpResponseBadRequest()
                        elif post.status == 4:
                            try:
                                line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage('画像を送信してください'),
                                )
                            except LineBotApiError:
                                return HttpResponseBadRequest()
                    else:
                        startButton(
                            event.reply_token,
                            'ご利用ありがとうございます\nメニューを更新したい場合、下のボタンを押してください\nなお、以下がサイトのURLです\n\nhttps://{}'.format(settings.DOMAIN_NAME)
                        )
                elif isinstance(event.message, ImageMessage):
                    if has_created == True:
                        if post.status == 4:
                            try:
                                message_content = line_bot_api.get_message_content(event.message.id)
                                with NamedTemporaryFile(mode='w+b') as f:
                                    for chunk in message_content.iter_content():
                                        f.write(chunk)
                                    post.image_path.save(event.message.id + '.jpg', File(f), save=True)
                                post.status = 5
                                post.save()
                            except:
                                traceback.print_exc()
                                try:
                                    line_bot_api.reply_message(
                                        event.reply_token,
                                        TextSendMessage('画像を保存できませんでした'),
                                    )
                                except LineBotApiError:
                                    return HttpResponseBadRequest()
                            confirmButton(
                                event.reply_token,
                                '項目は以上です\nこれでよろしければ「保存」、更新を中止したい場合は「中止」を押してください'
                            )

                        elif post.status == 0:
                            startButton(
                                event.reply_token,
                                'ご利用ありがとうございます\nメニューを更新したい場合、下のボタンを押してください\nなお、以下がサイトのURLです\n\nhttps://{}'.format(settings.DOMAIN_NAME)
                            )

                        elif post.status == 5:
                            confirmButton(
                                event.reply_token,
                                'すでに画像は送信されています\n更新または中止を選択してください'
                            )

                        else:
                            try:
                                line_bot_api.reply_message(
                                    event.reply_token,
                                    TextSendMessage('テキストを入力してください'),
                                )
                            except LineBotApiError:
                                return HttpResponseBadRequest()
                    else:
                        startButton(
                            event.reply_token,
                            'ご利用ありがとうございます\nメニューを更新したい場合、下のボタンを押してください\nなお、以下がサイトのURLです\n\nhttps://{}'.format(settings.DOMAIN_NAME)
                        )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
