import json
import os
import summarizer
from yattag import Doc, indent


def html_for_item(i, item, doc, tag, text, line):
    pos, neg = len(item.positive), len(item.negative)
    with tag('div', klass='layui-colla-item'):
        with tag('h2', klass='layui-colla-title'):
            doc.asis('&nbsp;&nbsp;')
            line('strong', item.lemma, style='color: #01AAED; font-size: 24px;')
            doc.asis('&nbsp;&nbsp;')
            with tag('span', style='color: #FF5722; font-size: 12px;'):
                with tag('i', klass='layui-icon'):
                    doc.asis('&#xe6c6;')
                text(pos)
            doc.asis('&nbsp;/&nbsp;')
            with tag('span', style='color: #2F4056; font-size: 12px;'):
                with tag('i', klass='layui-icon'):
                    doc.asis('&#xe6c5;')
                text(neg)
        with tag('div', klass='layui-colla-content' if i > 0 else 'layui-colla-content layui-show'):
            with tag('div', ('lay-showPercent', 'true'), klass='layui-progress', style='margin-top: 10px'):
                line('div', '', ('lay-percent', str(100 * pos // (pos + neg)) + '%'),
                     klass='layui-progress-bar layui-bg-red')
            doc.stag('hr')
            with tag('div'):
                line('strong', 'positive:')
            with tag('ul'):
                for n in item.positive[:5]:
                    with tag('li'):
                        line('span', '', klass='layui-badge-dot')
                        doc.asis('&nbsp;&nbsp;')
                        text(str(n.sent))
            doc.stag('hr')
            with tag('div'):
                line('strong', 'negative:')
            with tag('ul'):
                for n in item.negative[:5]:
                    with tag('li'):
                        line('span', '', klass='layui-badge-dot layui-bg-cyan')
                        doc.asis('&nbsp;&nbsp;')
                        text(str(n.sent))


def html(summary):
    data = str([{'value': len(item.positive) + len(item.negative), 'name': item.lemma} for item in summary[:8]])
    doc, tag, text, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('head'):
            doc.stag('meta', charset='utf-8')
            doc.stag('meta', name='viewport', content='width=device-width, initial-scale=1, maximum-scale=1')
            doc.stag('link', rel='stylesheet', href='http://cdn.90so.net/layui/2.2.5/css/layui.css')
        with tag('body'):
            with tag('div'):
                with tag('div', klass='layui-container'):
                    with tag('div', klass='layui-row', style='margin-top: 40px'):
                        with tag('div', klass='layui-col-md12'):
                            with tag('div', klass='layui-card'):
                                line('div', 'Reviews Summary', klass='layui-card-header layui-bg-green')
                                with tag('div', klass='layui-card-body'):
                                    with tag('div', klass='layui-row'):
                                        with tag('div', klass='layui-col-md6'):
                                            with tag('div', 'lay-accordion', klass='layui-collapse'):
                                                for i, item in enumerate(summary):
                                                    html_for_item(i, item, doc, tag, text, line)
                                        with tag('div', klass='layui-col-md6'):
                                            line('div', '', id='chart',
                                                 style='width: 500px; height: 500px; margin: 20px auto;')
            line('script', '', src='http://cdn.90so.net/layui/2.2.5/layui.all.js')
            line('script', '', src='https://cdnjs.cloudflare.com/ajax/libs/echarts/4.0.4/echarts-en.simple.min.js')
            line('script', 'var data = ' + data + ''';
                echarts.init(document.getElementById('chart')).setOption({
                    series: [
                        {
                            type: 'pie',
                            radius: '60%',
                            center: ['50%', '50%'],
                            data: data.reverse(),
                            roseType: 'radius',
                            animationType: 'scale',
                            animationEasing: 'elasticOut'
                        }
                    ]
                });
''')
    return indent(doc.getvalue())


while True:
    print('----------------------------------------')
    with open(input("please choose input file:")) as file:
        reviews = '\n\n'.join(item['review'] for item in json.load(file))
    print('parsing text ...')
    s = summarizer.Summarizer(reviews).summary()
    with open('summary.html', 'w') as file:
        file.write(html(s))
    print('please access file://' + os.path.abspath('summary.html'))
