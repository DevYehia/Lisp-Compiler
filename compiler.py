import tkinter as tk
import re
import pandas
import pandastable as pt

from LispParser import *
from LispScanner import *
from Tokens import *
import os


Tokens = []  # to add tokens to list
errors = []
tokens_List = []
delimiter_List = []




# GUI
root = tk.Tk()

canvas1 = tk.Canvas(root, width=400, height=300, relief='raised')
canvas1.pack()

label1 = tk.Label(root, text='Lispiler')
label1.config(font=('helvetica', 14))
canvas1.create_window(200, 25, window=label1)

label2 = tk.Label(root, text='Enter The File Name:')
label2.config(font=('helvetica', 10))
canvas1.create_window(200, 100, window=label2)

entry1 = tk.Entry(root)
canvas1.create_window(200, 140, window=entry1)


def Scan():
    x1 = entry1.get()
    f = open(x1,"r")
    for line in f.read().split("\n"):
        find_token(line,Tokens)
    df = pandas.DataFrame.from_records([t.to_dict() for t in Tokens])

    # to display token stream as table
    dTDa1 = tk.Toplevel()
    dTDa1.title('Token Stream')
    dTDaPT = pt.Table(dTDa1, dataframe=df, showtoolbar=True, showstatusbar=True)
    dTDaPT.show()
    tokens_List = Tokens_to_dict(Tokens)
    getDelimiters(tokens_List,delimiter_List)
    # start Parsing
    ParserTool = Parser(errors,tokens_List,delimiter_List)
    Node = ParserTool.Parse()
    Tokens.clear()
    tokens_List.clear()
    delimiter_List.clear()
    # to display errorlist
    df1 = pandas.DataFrame(errors)
    dTDa2 = tk.Toplevel()
    dTDa2.title('Error List')
    dTDaPT2 = pt.Table(dTDa2, dataframe=df1, showtoolbar=True, showstatusbar=True)
    errors.clear()
    dTDaPT2.show()
    Node.draw()

    # clear your list

    # label3 = tk.Label(root, text='Lexem ' + x1 + ' is:', font=('helvetica', 10))
    # canvas1.create_window(200, 210, window=label3)

    # label4 = tk.Label(root, text="Token_type"+x1, font=('helvetica', 10, 'bold'))
    # canvas1.create_window(200, 230, window=label4)


button1 = tk.Button(text='Scan', command=Scan, bg='brown', fg='white', font=('helvetica', 9, 'bold'))
canvas1.create_window(200, 180, window=button1)
root.mainloop()