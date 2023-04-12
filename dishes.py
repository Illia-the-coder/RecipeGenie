import openai
from pywebio.output import *
from pywebio.input import *
from pywebio import start_server, config
from telegraph import Telegraph
import markdown
import os

openai.api_key = os.environ['OPENAI_API_KEY']

telegraph = Telegraph()
telegraph.create_account(short_name='1337')


def create_tlgrph(title, text):
    tit = ' '.join(title.split()[:8])
    response = telegraph.create_page(
        tit,
        html_content=text.replace('\n', '<br>').replace('h1', 'h3').replace(
            'h2', 'h4').replace('span', '').replace('html', '')
    )
    link = f'<a href = "{response["url"]}">{tit}</a>'
    return link


def suggest_ingridients(ingridients):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Suggest ingredients based on: {ingridients}",
            temperature=0.3,
            max_tokens=3000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response['choices'][0]['text']
    except openai.exceptions.OpenAiError as e:
        print("An error occurred:", e)
        return None


def translate_text(text, lang='uk'):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Translate this into {lang}:\n\n{text}\n\n",
            temperature=0.3,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response['choices'][0]['text']
    except openai.exceptions.OpenAiError as e:
        print("An error occurred:", e)
        return None


def get_image(desc):
    response = openai.Image.create(
        prompt=desc +
        '(big,full,tasty,delicous,restaurant serving food photo with some text description)',
        n=3,
        size="1024x1024"
    )
    return response['data'][0]['url']


def get_recepi(ingridients, type='main', model='text-davinci-003'):
    try:
        response = openai.Completion.create(
            model=model,
            prompt=f"Write a {type} recipe based on these ingredients:\n\nIngredients:\n" +
            ingridients.replace(',', '\n')+"\n\n",
            temperature=0.3,
            max_tokens=120,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        text = response['choices'][0]['text']
        return text
    except openai.exceptions.OpenAiError as e:
        print("An error occurred:", e)
        return None, None


@config(title='Disher')
def page():
    md_t = ''
    put_markdown('# `Recepi finder`')
    md_t += '## `Recepi finder`'
    data = input_group("Dish info", [input('Choose ingridients:', name='ing'),
                                     select('Choose recipe type:', ['main', 'dessert', 'breakfast'], name='type_')])
    put_markdown(f"## `Our ingredients`: \n - " +
                 data['ing'].replace(',', '\n - '))
    md_t += f"## `Our ingredients`: \n - " + data['ing'].replace(',', '\n - ')
    ing_suggestion = suggest_ingridients(data['ing'])
    put_markdown(f"## `Ingredients suggestions`: {ing_suggestion}")
    md_t += f"## `Ingredients suggestions`: {ing_suggestion}"
    ing_type_user = select('Choose Ingredients suggested or Your ingredients',
                           ['Ingredients suggested', 'Your ingredients'])
    # popup('Loading recepi...')
    put_markdown('## `Recepi`')
    md_t += '## `Recepi`'
    ing_r = ing_suggestion if ing_type_user == 'Ingredients suggested' else data['ing']
    text = get_recepi(ing_r, data['type_'])
    put_markdown(text)
    md_t += text
    # popup('Loading image...')
    put_markdown('## `Probable image of dish`')
    md_t += '## `Probable image of dish`'
    image_url = get_image(text)
    put_image(image_url)
    md_t += f'<img src="{image_url}">'
    put_markdown('## `Telegraph link`')
    put_html(create_tlgrph(f'Recepi for dishes: {data["ing"]}', markdown.markdown(md_t)))


if __name__ == '__main__':
    start_server(page, port=8080)
