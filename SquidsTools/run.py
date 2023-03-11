import eel

if __name__ == '__main__':
    eel.init('web', allowed_extensions=['.js', '.html'])
    eel.start('index.html')
