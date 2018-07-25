# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:47:39 2016

@author: lssx
"""

#==================================================================================
# This software will identfy if an PLGS identified sequence is in violation of the pepsin cleavage rule as identified in:
# Y. Hamuro et al. Rapid Commun. Mass Spectrom. 2008; 22: 1041–1046
# (H,K,R,P in position P1' or P in P2')
# The seqeunce of the protein is required and can be loaded using a FASTA sequence and the load fasta function or just assigned to the fasta_seqeunce variable
# The .CSV output from LARS can be used to provide the list of identified peptides or any file adhering to the Waters Ion accounting .csv format
#==================================================================================

import csv 
import re
import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog
from tkinter import StringVar
from tkinter import ttk
from tkinter import Event
from tkinter import messagebox

global fasta_sequence

class ToolTip(object):
    """
    This class is a modified version of the one found here http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml
    it allows for the attachement of tool tip to entryboxes, labels and all other widgets from tkinter
    """

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        label = tk.Label(tw, text=self.text, justify="left",
                      background="#ffffe0", relief="solid", borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        """
        Removes the tool tip. Called upon exiting the widgets
        """
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def createToolTip(widget, text): 
        """
        Creates the tooltip from the tooltip class, and displays the text given to the function when the cursor enters 
        or exit the widget 
        """
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

class Application(tk.Frame):
    """
    """
    def __init__(self, root):
        """
        Class call --> Tkinter frame
        
        When the class is called the frame is initiated. The global values from the user input are made
        and defined. These values are used in the functioncs in the FunctionLibrary Class. 
        """
        tk.Frame.__init__(self, root)        
        #Scrollbar and startup geometry      
        self.canvas = tk.Canvas(root, width = 700, height = 310, borderwidth=0, background="gray94")
        self.frame = tk.Frame(self.canvas, background="gray94")
        self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4),window=self.frame, anchor="nw", tags="self.frame")
        self.frame.bind("<Configure>", self.OnFrameConfigure)
        self.frame.focus_force()
        #To allow the Popwindow to be a toplevel frame
        self.root = root
        #Initiating the widgets
        self.createWidgets()
        # Global variables are defined to be manipulated and transfered between Class's/Functions's
        self.index_pop_set = set() #Used to store the indexes of seqeunces violating the pepsin rule
        self.main_dict = {} #Used to store the read in LARS lines, thereby enabeling the storage of an index that can be used to remove all sequences violating the pepsin rule
        self.check_dict = {} #Used to identify peptides violating the pepsin rule

        # Menu constructor
        self.menubar = tk.Menu(self)
        #Help Menu
        menu = tk.Menu(self.menubar)        
        #menu.add_command(label = "Save", command = self.save)
        #menu.add_command(label = "Load", command = self.load)
        #menu.add_command(label = "About", command = self.About)
        self.menubar.add_cascade(label = "File", menu = menu)
        root.config(menu = self.menubar)
        #self.Dialog_insert("Hi there friend.\nThis is where i am going to show you the results of your LARS analysis.\nIf something goes wrong i should be able to help you fix it.\n\n")
    
    def OnFrameConfigure(self, event):
        '''
        Reset the scroll region to encompass the inner frame.
        '''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def createWidgets(self): 
        """
        All the widgets that are present when the frame is started are defined below. 
        """
                
        #The textbox for keeping track of the program's progress
        global Dialog
        Dialog_scrollbar = tk.Scrollbar(self.frame)
        Dialog_scrollbar.grid(row=3, column=7, rowspan =5, sticky='n,s')
        Dialog = tk.Text(self.frame, height = 11, relief = 'groove', bd = 2, width = 80, yscrollcommand=Dialog_scrollbar.set)
        Dialog.grid(column = 0, row = 3, columnspan = 4, rowspan = 5, sticky = "n,e", padx = 5, pady = 5)
        Dialog_scrollbar.config(command=Dialog.yview)
        Dialog.config(state=tk.DISABLED) #The box is keept in active so the user cannot write anything into it
        
        #The Add IA file Block
        self.Add_IA_text = tk.Label(self.frame, text = "")
        self.Add_IA_text.grid(column = 1, row = 0, padx = 5, pady = 5, sticky = "n, w",)
        self.Add_IA_Button = tk.Button(self.frame, text="Add IA File", command=self.load_LARS_output)
        self.Add_IA_Button.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = "n, w",)
        createToolTip(self.Add_IA_Button, "Add the Ion accounting file")
        #Block End
        #The Add Fasta Block
        self.Add_fasta_text = tk.Label(self.frame, text="")
        self.Add_fasta_text.grid(column = 1, row = 1, padx = 5, pady = 5, sticky = "n, w",)
        self.Add_fasta_button = tk.Button(self.frame, text="Add Fasta File", command=self.load_FASTA)
        self.Add_fasta_button.grid(column = 0, row = 1, padx = 5, pady = 5, sticky = "n, w",)
        createToolTip(self.Add_fasta_button, "Add the fasta sequence")
        #Block End
        #Run the filter
        self.filter_IA_Button =tk.Button(self.frame, text="Filter IA file", command=self.Process)
        self.filter_IA_Button.grid(column = 0, row = 2, padx = 5, pady = 5, sticky = "n, w",)
        
    def Dialog_insert(self, text):
        """
        text --> text inserted in a dialogbox
        
        This function is used to insert text into the dialogbox in the base GUI. The function works by unlocking the dialog box,
        inserting the desired text and closes the box for further input
        """
        Dialog.config(state=tk.NORMAL)
        Dialog.insert(tk.END, text)
        Dialog.see(tk.END)
        Dialog.config(state=tk.DISABLED)
            
    def Process(self):
        """
        This function determines what happens when the Process button is pressed
        When the Procces button is pressed the FunctionLibrary is called and the values typed into the boxes are stored
        """
        self.danger_list()
        self.remove_violations()

    def load_FASTA(self):
        """
        With this function the user can add the fasta file of the protein that the user is currently studying
        This is enables the user to use the Pepsin Cleavage filter  
        """
        
        fasta_filelocation = tk.filedialog.askopenfilename(filetypes =[("FASTA","*.fasta"), ('All files','*.*')])
        with open(fasta_filelocation) as fasta:
            global full_fasta
            global fasta_sequence       
            fasta_sequence = ''       
            full_fasta = fasta.readlines()
            if full_fasta[0][0] == '>': #Additional test to see if the file indeed is a fasta
                Regular_expression = re.compile(">.*\|.*\|(.+) OS.+") ## Can further be expanded so it test for matches with PLGS file
                match = re.match(Regular_expression, full_fasta[0])
                if match == None:
                    self.Add_fasta_text.config(text=full_fasta[0].rstrip("\n"))
                else:
                    self.Dialog_insert("Sequence for {0} was loaded \n".format(match.group(1)))   
                    self.Add_fasta_text.config(text = match.group(1))
                
                line_list = []
                for line in full_fasta[1:]:
                    line_list.append(line.rstrip('\n'))
                for item in line_list:
                    #print(item)
                    fasta_sequence += item
        fasta.close()
    
        
    def load_LARS_output(self): 
        """
        """
        global filelocation
        Regular_expression = re.compile('(\w.*)(_IA_final_peptide.csv)')
        filelocation = tk.filedialog.askopenfilename(filetypes =[("csv","_IA_final_peptide.csv"), ('All files','*.*')])
        if filelocation == '':
            self.Dialog_insert("No ion accounting file was added file was added")# Used to inform the user and prevent an error message
        else:
            #This block changes the working directory so the user will have fewer folders to press to load their files
            dir_list = filelocation.split('/')
            working_dict = ''
            for item in dir_list[:-2]:
                if item == dir_list[-3]:
                    working_dict += item
                else:
                    working_dict += "{0}/".format(item)
            os.chdir(working_dict)
            #Block end
            #This block saves the file path into the list that is used both in the save file and in the processing functions
            path = os.path.normpath(filelocation)
            elements_list = path.split('\\')
            pre_filename = elements_list[-1]
            match = re.match(Regular_expression, pre_filename)
            filename = match.group(1)
            global Prot_ident
            Prot_ident = filename
            self.Add_IA_text.config(text = Prot_ident)
            #Block end
        
    
    def danger_list(self):
        """
        """
        global fasta_length
        fasta_length = len(fasta_sequence)
        with open(filelocation) as csv_file:
            reader = csv.reader(csv_file)
            index = 0 #used to potentially remove any sequences that fails to meet a threshold
            for row in reader:
                if index == 0:
                    self.header = row
                    pass
                else:
                    position = int(row[26])
                    if position == 3:
                        cleavage_site =[-1, position-3, position-2, position-1, position, position+1, position+2, position+3,position+int(row[27])-2,position+int(row[27])-1]
                    elif position == 2:
                        cleavage_site =[-2, -1, position-2, position-1, position, position+1, position+2, position+3,position+int(row[27])-2,position+int(row[27])-1]
                    elif position == 1:
                        cleavage_site =[-3, -2, -1, position-1, position, position+1, position+2, position+3,position+int(row[27])-2,position+int(row[27])-1]
                    elif position == 0:
                        cleavage_site = [-4, -3, -2, -1, position, position+1, position+2, position+3,position+int(row[27])-2,position+int(row[27])-1]
                    elif (position+int(row[27])) == fasta_length:
                        cleavage_site = [position-4, position-3, position-2, position-1, position, position+1, position+2, position+3,position+int(row[27])-2,-1]
                    elif (position+int(row[27])) == (fasta_length-1):
                        cleavage_site = [position-4, position-3, position-2, position-1, position, position+1, position+2, position+3,-2,-1]
                    else:
                        cleavage_site = [position-4, position-3, position-2, position-1, position, position+1, position+2, position+3,position+int(row[27])-2,position+int(row[27])-1] #Adds cleavage sequence of each identified peptide
                    self.check_dict[index] = cleavage_site
                self.main_dict[index] = row
                index +=1
        csv_file.close()
        
        danger_list_P1 = []
        danger_list_P2 = []
        position = 0
        for char in fasta_sequence:
            if char in set(['R','H','K','P']):
                danger_list_P1.append((position))
                if char == 'P':
                    danger_list_P2.append((position))
            else: 
                pass
            position += 1
            
        self.write_set = set()
        keys = self.check_dict.keys()
        for key in keys:
            if self.check_dict[key][3] in danger_list_P1: #Tests the P1 position precceding the N-terminal of the identified peptide
                self.index_pop_set.add((key,'N'))
            elif self.check_dict[key][2] in danger_list_P2: #Test the P2 position precceding the N-terminal of the identified peptide
                self.index_pop_set.add((key,'N'))
            elif self.check_dict[key][-1] in danger_list_P1: #Test the P1 position in the C-terminal of the peptide
                self.index_pop_set.add((key,'C'))
            elif self.check_dict[key][-2] in danger_list_P2: #Test the P2 position P1 position in the C-terminal of the peptide
                self.index_pop_set.add((key,'C'))
            else:
                self.write_set.add(key)
    
    def remove_violations(self):
        """
        """
        global directory
        directory = tk.filedialog.askdirectory()        
        filtered__location = "{0}/{1}{2}".format(directory,Prot_ident,"_Pepsin_filtered_IA_peptide.csv")
        count = 0
        with open (filtered__location, 'w', newline = '') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.header)
            keys = self.main_dict.keys()
            for key in keys:
                for item in self.index_pop_set:
                    if key == item[0]:
                        count += 1
                        if item[1] == 'N':
                            self.Dialog_insert("{0}{1}|{2}\n".format(fasta_sequence[self.check_dict[key][2]],fasta_sequence[self.check_dict[key][3]],self.main_dict[key][24]))
                        elif item[1] == 'C':
                            self.Dialog_insert("{0}|\n".format(self.main_dict[key][24]))
                        else:
                            pass
                    else:
                        pass
            
            for item in self.write_set:
                writer.writerow(self.main_dict[item])
        self.Dialog_insert("{0} seqeunces were found in violation of the pepsin cleavage rule \n".format(count))
        csvfile.close()
        
        
        
# This section starts and adjusts the GUI window to the determined settings
root=tk.Tk()
root.wm_title("Pepsin Cleavage Violation Checker")
Application(root).pack(side="top", fill="both", expand=True)
root.mainloop()
