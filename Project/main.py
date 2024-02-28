import requests
import random
import tkinter as tk
from tkinter.font import Font
import os
import sys
from io import BytesIO
from PIL import Image, ImageTk
from bs4 import BeautifulSoup

global root
global num_evolutions
global current_digimon_choices
global name_of_digimon_display
global image_of_digimon

def create_digimon_list(element_list,length):
    digimon_names_and_links_list = []
    for i in range(length):
        a_element = element_list[i].find('a', href=True)

        if a_element:
            name = a_element.get_text(strip=True)
            link = a_element['href']
            digimon_names_and_links_list.append((name,link))
    return digimon_names_and_links_list

def load_new_choices(url):
    res = requests.get(url)
    htmlData = res.content
    parsedData = BeautifulSoup(htmlData, "html.parser")

    #Finds the table containing the potential digimon evolutions
    def has_specific_text(tag):
        return tag.name == 'td' and tag.text.strip() == 'Digivolves Into'
    digiheader_tr = parsedData.find(has_specific_text).find_parent('tr', class_='digiheader')
    table = digiheader_tr.find_parent()
    table = table.find_all('td', {'width': '30%'})
    return create_digimon_list(table,len(table))

def init_window():
    global root 
    root = tk.Tk()
    root.title("Digi-Evolution Simulator")
    evolve_button = tk.Button(root, text="Evolve", command=evolve_digimon)
    evolve_button.grid(row=2, column=0, padx=8, pady=4)

def display_image_from_url(url):
    global num_evolutions, image_of_digimon
    response = requests.get(url)
    image_data = Image.open(BytesIO(response.content)) #reformat images for better performance
    image_data = image_data.resize((192, 192), resample=Image.NEAREST)
    photo = ImageTk.PhotoImage(image_data)
    image_of_digimon = tk.Label(root, image=photo)
    image_of_digimon.image = photo 
    image_of_digimon.grid(row=1, column=num_evolutions, padx=8, pady=4)

def find_image_url_from_page(page_url):
    res = requests.get(page_url)
    htmlData = res.content 
    parsedData = BeautifulSoup(htmlData, "html.parser")
    image_element = parsedData.find('img', class_='dot')# topimg = higher detail ||| dot = pixel
    image_url = image_element.get('src')
    return image_url

def evolve_digimon():
    global current_digimon_choices, num_evolutions, name_of_digimon_display
    if len(current_digimon_choices) != 0:
        current_digimon = random.choice(current_digimon_choices) #The Current Digimon being displayed
        name_of_digimon_display = tk.Label(root,text= current_digimon[0], font=Font(family="Impact", size=14))
        name_of_digimon_display.grid(row = 0, column=num_evolutions, padx=8, pady=4)
        display_image_from_url(find_image_url_from_page(current_digimon[1]))
        current_digimon_choices = load_new_choices(current_digimon[1])
        num_evolutions +=1
    else:
        evolve_button = tk.Button(root, text="Reset", command=reset)
        evolve_button.grid(row=2, column=num_evolutions - 1, padx=8, pady=4)

def reset():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def main():
    init_window()
    global num_evolutions
    global current_digimon_choices
    num_evolutions = 0
    
    url = "https://digidb.io/digimon-list/"
    res = requests.get(url)
    htmlData = res.content
    parsedData = BeautifulSoup(htmlData, "html.parser")
    
    allDigimon = parsedData.find_all('td', {'width': '21%'})
    current_digimon_choices = create_digimon_list(allDigimon, 5)
    evolve_digimon()
    root.mainloop()
    
main()