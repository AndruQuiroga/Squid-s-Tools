import eel


def main():
    eel.init('./web', allowed_extensions=['.js', '.html'])
    eel.start('index.html')
