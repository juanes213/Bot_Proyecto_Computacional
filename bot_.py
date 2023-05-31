import os
import telebot
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

bot = telebot.TeleBot('6071757066:AAFwZtIwBEdpqvGaPwIV6pWTv9DMbr6y_To')

def load_stars():
    stars = []
    with open('stars.txt', 'r') as file:
        for line in file:
            data = line.strip().split()
            x, y, z = float(data[0]), float(data[1]), float(data[2])
            star_id = data[3]
            brightness = float(data[4])
            harvard_num = data[5]
            names = []
            if len(data) >= 7:
                names_data = ' '.join(data[6:]).split(';')
                for name in names_data:
                    names.extend([name.strip()])
            star = {'x': x, 'y': y, 'z': z, 'id': star_id, 'brightness': brightness, 'harvard_num': harvard_num, 'names': names}
            stars.append(star)
    return stars

def names_constellations():
    constellations = []
    constellations_folder = 'constellations'
    for filename in os.listdir(constellations_folder):
        if filename.endswith('.txt'):
            constellation_name = os.path.splitext(filename)[0]
            constellations.append(constellation_name)
    return constellations

def load_constellation_stars(constellation_name):
    constellation_file = os.path.join('constellations', f'{constellation_name}.txt')
    stars = []
    
    try:
        with open(constellation_file, 'r') as file:
            for line in file:
                star_pair = line.strip().split(',')
                if star_pair:
                    stars.extend(star_pair)
    except FileNotFoundError:
        # Si el archivo de la constelación no se encuentra, se retorna una lista vacía
        return []

    return stars


@bot.message_handler(commands=['estrellas'])
def show_stars(message):
    stars = load_stars()

    x_values = [star['x'] for star in stars]
    y_values = [star['y'] for star in stars]

    plt.figure()
    plt.scatter(x_values, y_values, marker='.', color='white', alpha=0.8, s=1)
    plt.gca().set_facecolor('black')
    plt.axis('off')

    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlim(min(x_values), max(x_values))
    plt.ylim(min(y_values), max(y_values))

    plt.savefig('stars_plot.png', facecolor='black', bbox_inches='tight', pad_inches=0)
    with open('stars_plot.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

@bot.message_handler(commands=['constelaciones'])
def show_constellations(message):
    constellations = names_constellations()

    if constellations:
        response = "Las constelaciones disponibles son:\n" + '\n'.join(constellations)
    else:
        response = "No se encontraron constelaciones disponibles."

    bot.reply_to(message, response)

@bot.message_handler(commands=['constelacion'])
def show_constellation_graph(message):
    try:
        constellation_name = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Por favor, proporciona el nombre de una constelación después del comando /constelacion.")
        return

    stars = load_stars()
    constellation_stars = load_constellation_stars(constellation_name)
    constellation_stars = [star_name.strip() for star_name in constellation_stars]

    # Verificar si la constelación existe
    if not constellation_stars:
        bot.reply_to(message, "La constelación no fue encontrada. Por favor, verifica el nombre e intenta nuevamente.")
        return
    # Crear una lista ordenada de nombres de estrellas de la constelación
    constellation_stars_ordered = []
    for star_name in constellation_stars:
        for star in stars:
            if star_name in star['names'] and star not in constellation_stars_ordered:
                constellation_stars_ordered.append(star)
                break

    constellation_stars_data = constellation_stars_ordered
    x_values = [star['x'] for star in stars]
    y_values = [star['y'] for star in stars]

    plt.figure()
    plt.scatter(x_values, y_values, marker='.', color='white', s=0.1)
    plt.gca().set_facecolor('black')

    # Conectar las estrellas de la constelación
    for i in range(len(constellation_stars_data) - 1):
        x1, y1 = constellation_stars_data[i]['x'], constellation_stars_data[i]['y']
        x2, y2 = constellation_stars_data[i + 1]['x'], constellation_stars_data[i + 1]['y']
        plt.plot([x1, x2], [y1, y2], color='red', linewidth=1)

    # Agregar la leyenda con el nombre de la constelación
    plt.text(0.5, -0.05, constellation_name, color='white', fontsize=12, ha='center', transform=plt.gca().transAxes)

    plt.axis('off')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlim(min(x_values), max(x_values))
    plt.ylim(min(y_values), max(y_values))

    plt.savefig('constellation_plot.png', facecolor='black', bbox_inches='tight', pad_inches=0)
    with open('constellation_plot.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

@bot.message_handler(commands=['todas'])
def show_all_stars_and_constellations(message):
    show_stars(message)
    constellations = names_constellations()
    for constellation in constellations:
        message.text = f"/constelacion {constellation}"
        show_constellation_graph(message)

@bot.message_handler(commands=['start', 'ayuda'])
def send_help(message):
    help_text = "¡Hola! Soy un bot de Telegram. Estas son mis funcionalidades:\n\n" \
                "/ayuda - Muestra esta ayuda\n" \
                "/estrellas - Muestra un gráfico de todas las estrellas\n" \
                "/constelaciones - Muestra los nombres de las constelaciones disponibles\n" \
                "/constelacion <nombre_constelacion> - Muestra un gráfico de una constelación específica\n" \
                "/todas - Muestra todas las estrellas y constelaciones \n" \
                "Por favor, utiliza los comandos siguiendo el formato adecuado."

    bot.reply_to(message, help_text)

@bot.message_handler(func=lambda message: True)
def handle_invalid_command(message):
    bot.reply_to(message, "Comando inválido. Por favor, utiliza uno de los comandos disponibles. Puedes usar /ayuda para ver la lista de comandos.")

bot.polling()
