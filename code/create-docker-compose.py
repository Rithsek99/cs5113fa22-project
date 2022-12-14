import argparse
try:
    import configparser
except:
    from six.moves import configparser

pokemon_emojis = ['\U0001F435', '\U0001F412', 
            '\U0001F98D', '\U0001F9A7', 
            '\U0001F436', '\U0001F415',
            '\U0001F9AE', '\U0001F429',
            '\U0001F99D', '\U0001F431',
            '\U0001F43B', '\U0001F425',
            '\U0001F983', '\U0001F9A2',
            '\U0001F99C', '\U0001F985',
            '\U0001F995', '\U0001F432',
            '\U0001F479', '\U0001F9DA',
            '\U0001F436', '\U0001F415',
            '\U0001F9AE', '\U0001F429',
            '\U0001F99D', '\U0001F431',
            '\U0001F43B', '\U0001F425',]
#Trainer emojis
trainer_emojis =[ '\U0001F600', '\U0001F603', 
            '\U0001F604', '\U0001F605', 
            '\U0001F606', '\U0001F602',
            '\U0001F923', '\U0001F642',
            '\U0001F643', '\U0001F609',
            '\U0001F607', '\U0001F60D',
            '\U0001F60A', '\U0001F617',
            '\U0001F3C6', '\U0001F3CA',
            '\U0001F3E0', '\U0001F3F0',
            '\U0001F9DB', '\U0001F43E',
            '\U0001F923', '\U0001F642',
            '\U0001F60A', '\U0001F617',
            '\U0001F604', '\U0001F605',
            '\U0001F60A', '\U0001F617']
config = {}
config['trainer'] = {}
config['pokemon'] = {}
def main(t, p):
    with open('docker-compose.yml', 'w') as f:
        f.write('version: "3.7"\n')
        f.write('services:\n')
        f.write('  server:\n')
        f.write('    build: .\n')
        f.write('    hostname: server\n')
        f.write('    networks:\n') 
        f.write('      - default\n')
        for i in range(t):
            f.write('  trainer'+str(i)+':\n')
            f.write('    build: .\n')
            f.write('    hostname: trainer'+str(i)+'\n')
            f.write('    networks:\n') 
            f.write('      - default\n')
            config['trainer']['trainer'+str(i)] = trainer_emojis[i]
        for i in range(p):
            f.write('  pokemon'+str(i)+':\n')
            f.write('    build: .\n')
            f.write('    hostname: pokemon'+str(i)+'\n')
            f.write('    networks:\n') 
            f.write('      - default\n')
            config['pokemon']['pokemon'+str(i)] = pokemon_emojis[i]
            
        # Create a ConfigParser object
        parser = configparser.ConfigParser()

        # Add the sections and their keys/values to the ConfigParser object
        for section, keys in config.items():
            parser.add_section(section)
            for key, value in keys.items():
                parser.set(section, key, value)
        
        parser.add_section('param')
        parser.set('param', 't', str(t))
        parser.set('param', 'p', str(p))
        parser.set('param', 'b', str(b))
        # Write the ConfigParser object to a config file
        with open('config.ini', 'w') as f:
            parser.write(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--b','--board-size', help='Description for size of the board', required=True)
    parser.add_argument('--t','--trainer', help='Description for number of the trainer', required=True)
    parser.add_argument('--p','--pokemon', help='Description for number of the pokemon', required=True)

    args = parser.parse_args()
    b, t, p = int(args.b), int(args.t), int(args.p)
    main(t, p)