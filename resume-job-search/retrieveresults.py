import random

all_star = [
    'Somebody once told me',
    'the world is gonna roll me',
    'I ain\'t the sharpest tool in the shed',
    'She was looking kinda dumb',
    'with her finger and her thumb',
    'in the shape of an \'L\' on her forehead',
    'Well the years start coming and they don\'t stop coming',
    'fed to the rules and I hit the ground running', 
    'Didn\'t make sense not to live for fun',
    'your brain gets smart but your head gets dumb',
    'So much to do so much to see',
    'so what\'s wrong with taking the back streets?',
    'You\'ll never know if you don\'t go',
    'you\'ll never shine if you don\'t glow',
    'Hey now, you\'re an all star',
    'get your game on, go play',
    'Hey now, you\'re a rock star',
    'get the show on, get paid',
    'And all that glitters is gold',
    'Only shooting stars break the mold'
    ]

def get_dummy_results():
    results = {}
    for i in range(len(all_star)):
        data_point = {
            'job-{}'.format(i): {
                'title': 'title-{}'.format(i),
                'short description': all_star[i],
                'random score': random.random()
                }
            }
        results.update(data_point)
    return results
