from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import pandas as pd
import os.path
import os
import numpy as np

import pymongo
from pymongo import MongoClient
from pymongo import errors

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
                                                NavigationToolbar2Tk)

# Create the main window and it's frames and widgets

# Create parent window, the root widget
root = Tk()
# Title of main window
root.title("Restaurant Inspections Data")
# Size of main window
root.geometry("500x600")
# Colour of main window
root.configure(background="#C0C0C0")
# Window doesn't change to fit the content
root.pack_propagate(False)

# Create frames in the parent window to hold each treeview widget to display 
# the data in each file that is loaded and the data from the analytics.
# Frame to display the inspections file data.
frame_data1 = LabelFrame(root, text = "Inspections data", background = 
                         "#C0C0C0")
frame_data1.place(height = 150, width = 500, rely = 0, relx = 0)

# Frame to display the violations file data
frame_data2 = LabelFrame(root, text = "Violations data", background =
                         "#C0C0C0")
frame_data2.place(height = 150, width = 500, rely = 0.25, relx = 0)

# Frame to display the analytics data
frame_data3 = LabelFrame(root, text = "Data results", background =
                         "#C0C0C0")
frame_data3.place(height = 150, width = 500, rely = 0.5, relx = 0)

# Frame to display the uplaod file button widgets and to display the file that 
# was opened last to the user.
frame_files = LabelFrame(root, text = "File open")
frame_files.place(height =100 , width = 500, rely = 0.8, relx = 0)

# Label widget inside the frame that updates which file is open, default set to 
# informing the user that no files have been loaded yet.
label_file = ttk.Label(frame_files, text = "no files selected")
label_file.place(rely = 0, relx = 0)

# Create tree widgets for each treeview frame created in the main window. 
# Set how much space the treeview takes up inside of the frame
tree1 = ttk.Treeview(frame_data1)
tree1.place(relheight = 0.9, relwidth = 1)

tree2 = ttk.Treeview(frame_data2)
tree2.place(relheight = 0.9, relwidth = 1)

tree3 = ttk.Treeview(frame_data3)
tree3.place(relheight = 0.9, relwidth = 1)

# Create Scrollbar widget for each treeview to scroll through the displayed 
# data vertically and horizontally, responds by the user event of clicking
# the mouse on the arrows, or click and drag on the bar, activating the tkinter
# method on the treeview object.
# Vertical scroll bar
tree_scrolly1 = Scrollbar(frame_data1, orient = "vertical", 
                          command = tree1.yview)
# Horizontal scroll bar
tree_scrollx1 = Scrollbar(frame_data1, orient = "horizontal", 
                          command = tree1.xview)

tree_scrolly2 = Scrollbar(frame_data2, orient = "vertical",
                          command = tree2.yview)
tree_scrollx2 = Scrollbar(frame_data2, orient = "horizontal", 
                          command = tree2.xview)

tree_scrolly3 = Scrollbar(frame_data3, orient = "vertical",
                          command = tree3.yview)
tree_scrollx3 = Scrollbar(frame_data3, orient = "horizontal", 
                          command = tree3.xview)

# Assign the scrollbars to their respective treeviews
tree1.configure(xscrollcommand = tree_scrollx1.set) 
tree1.configure(yscrollcommand = tree_scrolly1.set)
# Scrollbar to fill the size of the frame
tree_scrollx1.pack(side = "bottom", fill = "x")
tree_scrolly1.pack(side = "right", fill = "y")

tree2.configure(xscrollcommand = tree_scrollx2.set) 
tree2.configure(yscrollcommand = tree_scrolly2.set)
tree_scrollx2.pack(side = "bottom", fill = "x")
tree_scrolly2.pack(side = "right", fill = "y")
    
tree3.configure(xscrollcommand = tree_scrollx3.set) 
tree3.configure(yscrollcommand = tree_scrolly3.set)
tree_scrollx3.pack(side = "bottom", fill = "x")
tree_scrolly3.pack(side = "right", fill = "y")
        
# Create a menu widget in the main window
menu = Menu(root)
root.config(menu = menu)
    
# Create the menu items to the main menu, create 2, file and data
# remove the tear off dotted lines and change hover colour
file_items = Menu(menu, tearoff = 0, activebackground='#8b0000')
data_items = Menu(menu, tearoff = 0, activebackground = "#8b0000")
menu.add_cascade(label="File", menu = file_items)
menu.add_cascade(label = "Data", menu = data_items)
    
# Create drop down options for data menu, create two, statistics and graphs
# Disable the menus so that the user can not click them until the inspections 
# or the violations data has been loaded by the user.
# Create sub menu for statistics and graphs menu.
statistics_items = Menu(menu, tearoff = 0, activebackground='#8b0000')
graph_items = Menu(menu, tearoff = 0, activebackground='#8b0000')
data_items.add_cascade(label = "Statistics", state = "disable", 
                       menu = statistics_items)
data_items.add_cascade(label = "Graphs", state = "disable", 
                       menu = graph_items)

# A class for the event level of the app. The current state of the data can be
# accessed by different functions depending on what the user chooses from the
# GUI.
class Data:
    
    # Constructor
    def _init_(self, df_inspections, df_violations, df_statistics, value_entry1, 
               value_entry2, value_entry3):
        self.df_inspections = pd.DataFrame()
        self.df_violations = pd.Dataframe()
        self.df_statistics = pd.Dataframe()
        self.value_entry1 = ""
        self.value_entry2 = ""
        self.value_entry3 = ""

        
    def load_inspections(self):
    # When the user clicks the button to uplaod and clean the inspections.csv 
    # file, the widget's response to the event is to call this function. The 
    # function calls other functions within it. It uploads the inspections.csv 
    # from the local computer into the app, cleans the data and saves it to the 
    # mongo database. Changes the state of the statistics menu to active, so the 
    # user can now click it and run the analytics. The design choice to process it 
    # all automatically upon upload is to minimize potential user mistakes and 
    # increasing ease of use for the user, reducing the amount of actions the user 
    # needs to do themselves. Cleans to ensure the correct cleaning takes place and 
    # not left to the user to choose which cleaning to do and when, no other actions 
    # in the app can take place until the data is cleaned. Saved automatically to 
    # ensure the data is not lost if the application is closed and the user forgets 
    # or has not had chance to save it, the user has to repeat this process.
    # Cleaned and saved separately and not merged with violations file and saved as 
    # one to minimize the risk of the app closing down while the user has to upload 
    # the other file and the user can run the statistics analysis immediatly giving 
    # the user greater choice in the actions they wish to take.
    
        # Get the filename from the user
        filename = get_file_from_user()
        
        # Checks to see if the user chooses the correct filename, to the correct
        # button widget they chose in the GUI.
        if filename != 'Inspections.csv':  
            error(f"{filename} is incorrect, please choose inspections.csv")
        else:
            # Reads in the chosen file into a pandas dataframe and stores it in 
            # a member variable so it can be accessed from other functions.
            self.df_inspections = read_file(filename,['SERIAL NUMBER',
                                                      'ACTIVITY DATE',
                                                      'PROGRAM STATUS',
                                                      'PE DESCRIPTION',
                                                      'FACILITY ZIP', 
                                                      'SCORE'], dtype = 
                                            {'PROGRAM STATUS':'category'}, 
                                            parse_dates=['ACTIVITY DATE'])
            
            # Displays the dataframe in the GUI so the user can get visual
            # confirmation that the file has loaded into the app.
            display_tree(self.df_inspections, tree1)
            
            # Inform user the file has been loaded, informed here so limited
            # delay from the dataframe being displayed to user and the pop up
            # window
            info(f"{filename} has been uploaded")   
            
            # Cleans the data according to what the client needs.
            d1.clean_inspections_data()
            
            # Saves the data to mongo database.
            save_to_mongo(self.df_inspections, "Inspections")
            
            # Enables the disabled statistics menu widget, so the user can now 
            # run the analytics on the data if they want to.
            enable_statistics()
    
    
    def load_violations(self):
    # When the user clicks the button to uplaod and clean the violations.csv 
    # file the widget's response to the event is to call this function. The 
    # function calls other functions within it. It uploads the violations.csv from 
    # the local computer into the app, cleans the data and saves it to the mongo 
    # database. Changes the state of the graphs menu to activate it so the user can 
    # now click it and run the analytics. The design choice to process it all 
    # automatically upon upload is to minimize potential user mistakes and 
    # increasing the ease of use for the user, reducing the amount of actions the 
    # user needs to do themselves. Cleans to ensure the correct cleaning takes place 
    # and not left to the user to choose which cleaning to do and when, graph 
    # analytics can not take place until this data is cleaned. Saved automatically 
    # to ensure the data is not lost if the application is closed and the user forgets 
    # or has not had chance to save it, the user has to repeat this process.
        
        # Uploads inspections data from mongo database first, as it is needed to
        # clean the violations data. The violations data is merged to the inspections 
        # data to ensure that no outputs are from inactive restaurants.
        d1.upload_inspections_from_mongo()
        info("Loaded Inspections file as needed for cleaning violations,...please wait")
        
        # If inspections.csv has not been loaded yet, warns the user to 
        # upload it first and exits the function
        if self.df_inspections.empty:
            label_file["text"] = "No file exists"
            error("Please upload inspections.csv before violations.csv")
        else:
            # Gets the filename from the user
            filename =  get_file_from_user()
            
            # Checks that it's the correct filename according to the widget the
            # user clicked
            if filename != 'violations.csv':
                error(f"{filename} is incorrect, please choose violations.csv")
            else:
                # Reads in the file into a pandas dataframe
                self.df_violations = read_file(filename,['SERIAL NUMBER', 
                                                        'VIOLATION CODE', 
                                                        'VIOLATION DESCRIPTION'])
            
                # Displays the data to the user, for visual confirmation that the 
                # file has been uploaded
                display_tree(self.df_violations, tree2)
                
                # Cleans the data
                d1.clean_violations_data()
                
                # Saves the data to mongo database
                save_to_mongo(self.df_violations, "Violations")
                
                # Enables the menu widget to run the analytics for the graph 
                # visuals
                enable_graphs()
            
            
    def clean_inspections_data(self):
    # Further clean the data in the inspections file. Missing values
    # found in 'score' series are not dealt with in this function. Checked 
    # for missing values in the inspection's dataframe by df.isnull().sum
    # () and found 151 in the score column due to the low percentage of 
    # missing values ignore them no need to inpute which would slow the 
    # program compared to the benefits. Ignoring them happens when running 
    # the statistics' functions, can't ignore permanantly as those rows are
    # needed for different analysis.
      
        # Inform the user of what is happening due to the time taken for cleaning
        # to take place immediately after uploading the file, on the same event.
        info("Your data is being cleaned, please wait.....")
        # Remove all the rows/vendors that are inactive as per the client brief 
        # and reset the index of the dataframe so the index runs sequentially
        self.df_inspections = self.df_inspections.drop\
        (self.df_inspections[self.df_inspections['PROGRAM STATUS']== 'INACTIVE']\
         .index)
            
        self.df_inspections = self.df_inspections.reset_index(drop = True)
           
        # Remove the status column as no longer needed, knowing that only
        # active rows are available. Reduces the time to import and export the
        # data from mongo and to run the analytics.
        self.df_inspections = self.df_inspections.drop('PROGRAM STATUS', axis = 1)
        # Search for string inside of brackets in each value in PE 
        # DESCRIPTION column and add that string to a new column called 
        # seating type. As per the client brief.
        self.df_inspections['SEATING TYPE'] = self.df_inspections\
        ['PE DESCRIPTION'].apply(lambda st: st[st.find("(")+1:st.find(")")])
        # Remove the string within the brackets in the PE DESCRIPTION 
        # column by replacing it with an empty string.As per the clients 
        # brief so the data is not repeated in two columns.
        self.df_inspections["PE DESCRIPTION"] = self.df_inspections\
        ["PE DESCRIPTION"].str.replace(r"\(.*?\)","")

        # List of strings that were added to the new SEATING TYPE column because 
        # there was missing data inside of the brackets and thus data outside of
        # the bracket was added instead.
        strings = ['PRIVATE SCHOOL CAFETERI', 'FOOD MARKET WHOLESAL',
                   'SWAP MEET PREPACKAGED FOOD STAN',
                   'WHOLESALE FOOD COMPLE']
            
        # Replace the strings with an empty string and ignore those rows when
        # running the analytics
        for string in strings:
            self.df_inspections['SEATING TYPE'] = self.df_inspections\
            ['SEATING TYPE'].str.replace(string, "")

        # Remove the delivery routes from the zip codes so the zip codes 
        # can be grouped more accurately when running the analytics 
        # on number of violations per vendor per zip code.(As per client's 
        # brief) Facility Zip was chosen because there were no missing values
        # in this column
        self.df_inspections['FACILITY ZIP'] = self.df_inspections['FACILITY ZIP']\
        .str[:5]
        # Extract just the year from the date, this is all that is needed 
        # for the analytics later on. Reduces memory usage and speed of 
        # grouping the dataframe
        self.df_inspections['ACTIVITY DATE'] = self.df_inspections\
        ['ACTIVITY DATE'].dt.year
            
        # Reorder the columns for increased readability in JSON format inside
        # of mongo database
        self.df_inspections = self.df_inspections
        [['SERIAL NUMBER', 'FACILITY ZIP','ACTIVITY DATE','PE DESCRIPTION',
          'SEATING TYPE', 'SCORE']]
            
        # Display the cleaned data to the user in the tree widget.
        display_tree(self.df_inspections, tree1)
            
        info("Your data has been cleaned")
        
        
    def clean_violations_data(self):
    # Further clean the violations data. Join the data from both files into 
    # one dataframe so only the serial numbers from the violations file
    # that match the inspections file are used ensuring only active 
    # restaurants data is used, as per the brief. This data can then be used
    # to run some of the analytics later on, that needs data from both files.
        
        # Keep user informed as data is loaded and cleaned from one event
        # which takes time
        info("Cleaning data, please wait...")
        
        # Match the serial numbers as this is the common data identifying 
        # the specific restaurant and discard any data that doesn't match
        self.df_violations = self.df_inspections.merge(self.df_violations, 
                                                       on = 'SERIAL NUMBER')
        
        # Drop columns not needed for the analytics of this data, to decrease
        # memory when importing and exporting from mongo and increase speed
        # during analysing
        self.df_violations = self.df_violations.drop(['ACTIVITY DATE',
                                                      'PE DESCRIPTION','SCORE', 
                                                      'SEATING TYPE'], 
                                                     axis = 1)
        
        # Reorder columns for increased readability in JSON format when saved
        # in mongo
        self.df_violations = self.df_violations[['SERIAL NUMBER',
                                                 'VIOLATION CODE'
                                                 ,'VIOLATION DESCRIPTION',
                                                 'FACILITY ZIP']]
  
        # Display the cleaned data to the user in the tree widget
        display_tree(self.df_violations, tree2)
        
        info("Data has been cleaned")
        
    
    def upload_inspections_from_mongo(self):
    # Export the data for the inspections file from mongo database when the 
    # user wants to open the data in the GUI
        
        # Export the data from mongo database
        self.df_inspections = d1.upload_from_mongo('Inspections')
        
        # Inform the user if the file does not exist and needs to be
        # uploaded first
        if self.df_inspections.empty:
            label_file["text"] = "Data does not exist"
            
        else:
            # Display the file to the user, so they can view the data
            # and get visual confirmation the correct file has been loaded
            display_tree(self.df_inspections, tree1)
            info(f"file has been loaded")
            # Activate the widget to run the statistics. The widget is 
            # activated after the file has been loaded from the database
            # or from the local machine, so the user can run the analytics.
            enable_statistics()

            
    def upload_violations_from_mongo(self):
    # Export the cleaned data from the violations file from mongo database when 
    # the user wants to open the data in the GUI
        
        # Inform the user of what is happening as a quick response, so the user
        # isn't left waiting
        info("File loading...")
        
        # Export data from the database as a dataframe and store in the member 
        # variable to update it's current state
        self.df_violations = d1.upload_from_mongo('Violations')
        
        # Inform the user in the GUI that the data does not exist
        if self.df_violations.empty:
            label_file["text"] = "Data does not exist"
            
        else:
            # Display the data in the GUI for the user to look at
            display_tree(self.df_violations, tree2)
            
            # Enable the widget so the user can choose to run the analytics on 
            # this data and display the graph
            enable_graphs()
        
    
    def upload_from_mongo(self, collection_name):
    # Reads the data from the database and stores into pandas' dataframe. The 
    # collection name is passed in as an argument to identify which data the 
    # user requests. Inspections or violations. The user can load the data from 
    # the database incase they shut the program down after the data is uploaded 
    # from the local machine and the user doesn't have to repeat that process.

        # Connect to Mongo
        db = connect_to_mongo('localhost', 27017)['restaurant_inspections']
        
        # Get the relevant collection from the database that the user has 
        # requested through the GUI. Make a query to the collection and delete 
        # the document id. Returns the cursor
        cursor = db[collection_name].find({}, {'_id': False})
 
        # Converting cursor to a list of dictionaries and puts it into a 
        # dataframe
        df =  pd.DataFrame(list(cursor))
        
        # Checks to see if the data has been imported to mongo and informs the 
        # user if not as a pop up window and in the label widget in the main GUI 
        # window
        if df.empty:
            label_file["text"] = "Data does not exist"
            error(f"{collection_name} does not exist")
            info("Please upload your file")
        
        else:
            # Informs the user in the GUI which collection has been exported to 
            # the app
            label_file["text"] = collection_name

        return df
    
    
    def mean_score(self, column_name):
    # Calculates mean score per year per the different df series, according to 
    # the brief. There are missing values in the data for score but .mean() 
    # ignores missing values by default.
        # Ignores the missing values in the new column created in 
        # the data during cleaning, seating type.Ignores them rather 
        # than deletes the row as will need the 
        # data from those rows in other calculations.
        if column_name == "SEATING TYPE":
            d1.ignore_seating_missing_values()
        else:
            # Stores dataframe in different variable to preserve the current 
            # state df_inspections data for other calculations
            self.df_statistics = self.df_inspections
        
        # Groups the data according to which variable the user choses in the 
        # GUI.Either zipcode or seating type The variable is passed in the 
        # paramater in the function call of the widget that receives the event 
        # from the user and runs the mean calculation on scores for each group. 
        self.df_statistics = self.df_statistics.groupby\
        ([column_name, "ACTIVITY DATE"]).mean()["SCORE"].reset_index\
        (name = 'MEAN SCORE PER YEAR').round(decimals=2)
        
        # Display the results to the user in the GUI.
        display_tree(self.df_statistics, tree3)
        
        # Opens a new window in the GUI where the user can manipulate the range 
        # of the values calculated in the dataframe
        d1.user_input_window(column_name, 'MEAN SCORE PER YEAR')
        
              
    def median_score(self, column_name):
    # Calculates median score per year per the different df series, according 
    # to the brief. - See mean_score() for more details.
    
        # Ignores the missing values in the new column created in 
        # the data during cleaning, seating type.Ignores them rather 
        # than deletes the row as will need the 
        # data from those rows in other calculations.
        if column_name == "SEATING TYPE":
            d1.ignore_seating_missing_values()
        else:
            # stores dataframe in different variable to preserve the current 
            # state df_inspections data for other calculations
            self.df_statistics = self.df_inspections
        
        # Groups the data according to which variable the user choses in the GUI.
        # Either zipcode or seating type
        # The variable is passed in the paramater in the function call of the 
        # widget that receives the event from the user and runs the median 
        # calculation on scores for each group.
        self.df_statistics = self.df_statistics.groupby\
        ([column_name, "ACTIVITY DATE"]).median()['SCORE'].reset_index\
        (name = 'MEDIAN SCORE PER YEAR')
         
        # Displays the results in the GUI
        display_tree(self.df_statistics, tree3)
        
        # Opens a new window for the user to manipulate the range of values
        d1.user_input_window(column_name, 'MEDIAN SCORE PER YEAR')
        
   
    def mode_score(self, column_name):
    # Calculates the mode score per year per the different df series, according 
    # to the brief. - See mean_score() for more details.
       
        if column_name == "SEATING TYPE":
            d1.ignore_seating_missing_values()
        else:
            # stores dataframe in different variable to preserve the current 
            # state df_inspections data for other calculations
            self.df_statistics = self.df_inspections
        
        # Groups the data according to which variable the user choses in the 
        # GUI.Either zipcode or seating type The variable is passed in the 
        # paramater in the function call of the widget that receives the event 
        # from the user and runs the mode calculation on scores for each group.
        self.df_statistics = self.df_statistics.groupby([column_name,
                                                          "ACTIVITY DATE"])\
                             ['SCORE'].agg(pd.Series.mode).reset_index\
                             (name = 'MODE SCORE PER YEAR')

        # Displays the results in the GUI
        display_tree(self.df_statistics, tree3)
        
        # Opens a new window for the user to manipulate the range of values
        d1.user_input_window_mode(column_name)
        
     
    def ignore_seating_missing_values(self):
    # Ignores the missing values in the seating type by dropping the rows 
    # in the dataframe that have value of an empty string. There were 12 
    # missing values in the brackets in PE DESCRIPTION as a result, when 
    # moving to the new column the string outside the brackets was moved 
    # instead.They were converted to empty string during cleaning then the row 
    # dropped here
        self.df_statistics = self.df_inspections.drop(self.df_inspections[self.df_inspections['SEATING TYPE'] == ''].index)
        return self.df_statistics
        
    def user_input_window(self, column_name, column_name1):
    # The new window with the entry widgets for the user to manipulate the 
    # range of values in the mean/median/mode calculations, this is opened 
    # automatically after the first calculations are done. User can close
    # down the window if not needed.
        window_user = Tk()
        window_user.geometry("200x250")
        window_user.title("Change range of values")
        window_user.configure(background="#C0C0C0")
        
        # label widget for the entry widget. User can view certain seating 
        # types or zip codes
        value_label1 = Label(window_user, text=f"Enter {column_name} value")
        value_label1.grid(row = 1, column = 2, pady=2)
        # User inputs their choice in the entry widget
        self.value_entry1 = Entry(window_user)
        self.value_entry1.grid(row = 2, column = 2, pady=2)
        
        # When the button is pressed by the user, the reaction to the event
        # is a call to the function to process the users entry
        submit_button1 = Button(window_user, text='Submit', bg = "#8b0000", fg
                               = "white", command = lambda: 
                               d1.manipulate_values(column_name))
        submit_button1.grid(row = 3, column = 2, pady = 4)
        
        # Label widget for min range score per year value
        value_label2 = Label(window_user, text = "Enter min score value")
        value_label2.grid(row = 4, column = 2, pady = (4,2))
        
        # Entry loction for min value
        self.value_entry2 = Entry(window_user)
        self.value_entry2.grid(row = 5, column = 2, pady= (2,4))
        
        # Label widget for max range score per year value
        value_label3 = Label(window_user, text = "Enter max score value")
        value_label3.grid(row = 6, column = 2, pady = (4,2))
        
        # Entry location for the max score value
        self.value_entry3 = Entry(window_user)
        self.value_entry3.grid(row = 7, column = 2, pady= (2,4))
  
        # Button widget that calls the function to manipuate the values when 
        # user clicks it
        submit_button2 = Button(window_user, text='Submit', bg = "#8b0000", fg
                               = "white", command = lambda: 
                               d1.manipulate_score_values(column_name1))
        submit_button2.grid(row = 8, column = 2, pady = 4, padx = 4)
        
        # User can reset the dataframe to the original calculation.
        reset_button = Button(window_user, text='Reset', bg = "#8b0000", fg = 
                              "white", command = lambda: 
                              display_tree(self.df_statistics, tree3))
        reset_button.grid(row = 9, column = 2, pady = 4, padx = 4)
        
         
    def manipulate_values(self, column_name):
    # User can search for calculations for certain seating type or zipcode    
        # Gets the value entered by the user  
        value = self.value_entry1.get()
        
        # Checks the value entered is in the dataframe. The user can leave the 
        # entry blank so no check for that. All the rows that have the chosen 
        # value are put into a new dataframe.
        if value in self.df_statistics.values:
            df = self.df_statistics.loc[self.df_statistics[column_name] == 
                                    value]
            # Displayed to the user in the GUI
            display_tree(df, tree2)
        
        else:
            error("Out of range, please enter a different value")
    
    
    def manipulate_score_values(self, column_name1):
    # Manipulates the range of score per year values
        # Checks that the value entered is a digit, put in try catch as value 
        # needs to be checked as soon as it is retrieved.
        try:
            min = float(self.value_entry2.get())
            max = float(self.value_entry3.get())
            # Check if users' values are in the database and if the min value 
            # is less than the max value. Creates a new dataframe with the score 
            # per year values between the ranges the user has chosen
            if min <= max and min and max in self.df_statistics.values:
                df = self.df_statistics[self.df_statistics\
                                        [column_name1].between\
                                        (min, max)]
                # Display the results to the user in the GUI
                display_tree(df, tree3)
            else:
                error("Out of range, please enter a different value")
        except ValueError:
            error("Please enter a digit")
            
    def user_input_window_mode(self, column_name):
        # The new window with the entry widgets for the user to manipulate the 
    # range of values in the mean/median/mode calculations, this is opened 
    # automatically after the first calculations are done. User can close
    # down the window if not needed.
        window_user = Tk()
        window_user.geometry("150x150")
        window_user.title("Change range of values")
        window_user.configure(background="#C0C0C0")
        
        # label widget for the entry widget. User can view certain seating 
        # types or zip codes
        value_label1 = Label(window_user, text=f"Enter {column_name} value")
        value_label1.grid(row = 1, column = 2, pady=2)
        # User inputs their choice in the entry widget
        self.value_entry1 = Entry(window_user)
        self.value_entry1.grid(row = 2, column = 2, pady=2)
        
        # When the button is pressed by the user, the reaction to the event
        # is a call to the function to process the users entry
        submit_button1 = Button(window_user, text='Submit', bg = "#8b0000", fg
                               = "white", command = lambda: 
                               d1.manipulate_values(column_name))
        submit_button1.grid(row = 3, column = 2, pady = 4)
        
         
    def count_establishment_per_violation(self):
        # A bar chart that displays the number of establishments that have 
        # committed each type of violation.
        
        # Uses the violations data, groups the dataframe into violation codes 
        # and counts the establishments by their unique serial number and puts 
        # the count figure in a new column and sorts the column in ascending 
        # order for better visuals of the data
        self.df_visuals = self.df_violations.groupby(['VIOLATION CODE'])\
        .count()['SERIAL NUMBER'].reset_index\
        (name = 'NUMBER OF ESTABLISHMENTS').sort_values\
        ('NUMBER OF ESTABLISHMENTS')
        
        # THe window to display the graph
        graph_window()
        
        # Display the graph, passing in the columns needed for the axis, 
        # title of the graph and the type of graph
        d1.display_graph('NUMBER OF ESTABLISHMENTS','VIOLATION CODE', 
                         "Number of establishments commiting each violation"
                         , plt.bar) 
        
        
    def violations_per_establishment_per_zipcode(self):
    # A graph to display any colleration between violations per zip code and 
    # area.
        
        # Group the dataframe into zip code and then into the establishment
        # referenced by their serial number. Count the number of times each 
        # violation happens and rename the count column to display in the 
        # graph
        self.df_visuals = self.df_violations.groupby(['FACILITY ZIP',
                                                      'SERIAL NUMBER'])\
        .count()['VIOLATION CODE'].reset_index(name = 'VIOLATIONS PER VENDOR')
        
        # Calculate the mean in the violations per vendor and sort in ascending 
        # order for better understanding and better visuals of any correlations.
        self.df_visuals = self.df_visuals.groupby(['FACILITY ZIP']).mean()\
        ['VIOLATIONS PER VENDOR'].reset_index\
        (name = 'MEAN VIOLATIONS PER VENDOR').sort_values\
        ('MEAN VIOLATIONS PER VENDOR')
    
        # Open a window to display the graph
        graph_window()
    
        # Display the graph, passing in the columns needed for the axis, title 
        # of the graph and the type of graph
        d1.display_graph('MEAN VIOLATIONS PER VENDOR','FACILITY ZIP',
                         "Mean number of violations per vendor per zip code", 
                         plt.plot)


    def display_graph(self, column_y, column_x, title, plot_type):
    # Displays the graph from the manipulated pandas dataframe
      
        # Graph axis, passing in the column name depending on which graph
        # is needed
        x = self.df_visuals[column_x]
        y = self.df_visuals[column_y]
    
        # Produces the plot, either bar or line depending on which analytics the
        # user chooses to run
        plot_type(x,y, color = "#8b0000")
    
        # Reduces the size of the ticks and rotates for ease of reading. There 
        # are many ticks, zip codes, in the number of violations per vendor per 
        # zip code, so ease of reading them is not so great at first, but due to 
        # the ability to zoom in from the navigation bar, I decided it was ok.
        plt.xticks(fontsize = 6, rotation = 90)
        
        # Label the axis
        plt.xlabel(column_x)
        plt.ylabel(column_y)
    
        # Remove the margins between graph and axis to optimize the space in the 
        # window
        plt.margins(x=0)
    
        # Title of the graph
        plt.title(title, fontsize=18)

        
def graph_window():
# The window to hold the canvas for the graphs.
    window = Tk()
    
    window.title('Data Visuals') 
        
    # Set the size of the chart
    figure = plt.figure(figsize=(60,5), dpi =100)
    
    # Create the canvas
    canvas = FigureCanvasTkAgg(figure, window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    # Creates a Toolbar on the canvas which allows the user to manipulate 
    # the range of values in the
    # graph by zooming into sections of the graph
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    canvas._tkcanvas.pack()  
        
        
def get_file_from_user():
# Gets the file from the users local machine
    # Gui goes straight into the users file directory, for ease of use for the 
    # user
    root.filename = filedialog.askopenfilename()
    # Get the name of the file and remove the path
    filename = os.path.basename(root.filename)
    
    return filename
     
    
def read_file(filename, use_cols, *args, **kwargs):
# Simultaneously reads in the users file and partially cleans it.
# Only reading in Inspections and Violations file as Inventroy data is not 
# needed for the analysis.
    # Updates the user on what is happening due to the fact a lot happnes from
    # one click of a button and there is a wait for the user.
    info(f"Uploading {filename}, please wait...")
    # Optional arguments, depending on which file is entered by the user
    d_type = kwargs.get('dtype', None)
    parse_dates = kwargs.get('parse_dates', None)
    
    # Checks for non-default missing data and converts them to pandas' NAN. 
    # There isn't any in the original data but incase of missing values if 
    # data is added in the future.
    na_value = ["na", "--", "."]

    # Reads the data needed for the clients specifications only and not the 
    # whole file, to save on memory and increase speed when analysing the 
    # data and saving it into the database.Converts datatypes to reduce 
    # memory usage. Checks for and ignores lines of completely missing data
    # Dates are recognized as an object datatype when the csv file is being 
    # loaded, parse the dates by identifying each componets of the date as a 
    # string so it converts to a recognised date. 
    # Try catch to check for errors internally when reading in the file
    try:
        df = pd.read_csv(filename, usecols = use_cols, na_values = na_value,  
                         dtype = d_type, skip_blank_lines = True, parse_dates 
                         = parse_dates)
    
        label_file["text"] = filename
      
    except ValueError:
        error("The file is invalid")
        return None
    except FileNotFoundError:
        error(f"{filename} does not exist")
        
    return df
       
    
def save_to_mongo(df, collection_name):
# Saves the uploaded and cleaned data into the mongo database so the user can
# come back to the program after it has been closed to run the analytics.
    
    # Save to mongo database in chunks as the data is too large to save in one 
    # go. Convert each chunk of dataframe into a list of dictionaries. Each 
    # dictionary in the list is a row in the dataframe, the key as the column 
    # title and the value as the row.The list of dictionaries are then 
    # inserted into the database. During insertion, each dictionary is 
    # serialized and encoded into BSON format - Binary representation of JSON 
    # format, which offers more compact storage and quicker transmission when 
    # stored in the database. 
    # Call the function to connect to mongo and create a database
    info("Saving data...")
    db = connect_to_mongo('localhost', 27017)['restaurant_inspections']
    # Create collection
    collection = db[collection_name]
    
    # Check to see if the collection name already exists, warn the user 
    # if it does and come out of the function, so the user can not save twice
    collection_list = db.list_collection_names()
    if collection_name in collection_list:
        error(f"{collection_name} has already been saved")
    else:
        # Save to mongo database in chunks as the data is too large to save in 
        # one go Call the function to split the dataframe into 100 row chunks 
        # and iterate over each chunk
        for i in chunk_df(df, 100):
            # Convert each chunk of dataframe into a list of dictionaries. Each 
            # dictionary in the list is a row in the dataframe, the key as the 
            # column title and the value as the row.The list of dictionaries are 
            # then inserted into the database. During insertion, each dictionary 
            # is serialized and encoded into BSON format - Binary representation 
            # of JSON format, which offers more compact storage and quicker 
            # transmission when stored in the database. 
            collection.insert_many(i.to_dict('records'))
        info(f"Saved as {collection_name}")    

        
def connect_to_mongo(host, port):
# Connect to mongo
    # Put into a function as used in importing and exporting from the database
    # Check for errors
    try:
        client = MongoClient(host, port)
        print("\n Connection to mongo is successful \n")
    except ConnectionFailure:
        error("Saving has failed")
        print("Connection failed\n")
    
    return client        
        

def chunk_df(df, size):
# Split the dataframe into chunks so it can be saved into the database 
# without overloading the memory
    
    # Iterate over the number of rows wanted in each chunk and return that 
    # section of dataframe
    return (df[i:i + size] for i in range(0, len(df), size))
   
        
def display_tree(df,tree):
# Displays the pandas dataframe to the user in the GUI       
    # Clear any existing data that is in the tree widget
    tree.delete(*tree.get_children())

    # Assign the columns of the treeview as the pandas' dataframe columns 
    tree["column"] = list(df.columns)
    
    # Hide the tree view default column
    tree["show"] = "headings"
    
    # Create the headings for each column in the tree view
    for column in tree["columns"]:
        tree.heading(column, text = column)
        
    # Add the data to the columns
    # Transform each row of the dataframe into a list, the dataframe becomes
    # a list of lists
    df_rows = df.to_numpy().tolist()
    
    # Insert each list into the tree widget
    for row in df_rows:
        tree.insert("", "end", values = row)
                         
def error(text):
# Error pop up window to display to the user in the GUI
    messagebox.showerror("Error", text)
 
def info(text):
# Info pop up window to display to the user in the GUI
    messagebox.showinfo("Information", text)

def enable_statistics():
# The files need to be loaded in order for the analytics to be ran, the widget
# that lets the user choose this option is disabled until the files are either 
# uploaded or loaded from the database. As to not waist the users time.
    data_items.entryconfig("Statistics", state = "normal")
   
def enable_graphs():
# Activates the disabled widget for the analytics that run the graph visuals 
    data_items.entryconfig("Graphs", state = "normal")
    
def exit_application():
# Closes the application asks user for confirmation to prevent accidental 
# shutdown
    message = messagebox.askquestion ('Exit Application',
                                      'Are you sure you want to exit the application',
                                      icon = 'warning')
    if message == 'yes':
        root.destroy()
    
       
# Create an instance of the class to call the functions that respond to the 
# specific users' event, clicking the mouse. binding.
d1 = Data() 

# Create drop down options for file menu, create two, open and exit.
# Open allows the user to click onto more options and exit responds
# to the users' click, by exiting the program
# Create sub menu for open menu
open_items = Menu(menu, tearoff = 0, activebackground='#8b0000')
file_items.add_cascade(label = "Open", menu = open_items)
file_items.add_command(label = "Exit", command = exit_application)


# Create sub menu for open menu. When the user clicks on the labels, it 
# triggers a call to the function to load the respective files from the mongo 
# database into the app.
open_items.add_command(label="Inspections", command = lambda: 
                       d1.upload_inspections_from_mongo())
open_items.add_command(label="Violations", command = lambda: 
                       d1.upload_violations_from_mongo())

# Create the menus for the statistics sub menus
mean_list = Menu(menu, tearoff = 0, activebackground='#8b0000')
median_list = Menu(menu, tearoff = 0, activebackground='#8b0000')
mode_list = Menu(menu, tearoff = 0, activebackground='#8b0000')

statistics_items.add_cascade(label = "mean", menu = mean_list )
statistics_items.add_cascade(label = "median", menu = median_list)
statistics_items.add_cascade(label = "mode", menu = mode_list)

# Create the sub menu for mean
# For each of these sub menus. The event, the user clicking the menu item,
# triggers the call to the functon which calculates the mean, mode and median 
# for the inspection score per year and displays the results
mean_list.add_command(label = "seating type", command = lambda: 
                      d1.mean_score("SEATING TYPE"))
mean_list.add_command(label = "zip code" , command = lambda: 
                      d1.mean_score("FACILITY ZIP"))

# Create sub menu for median
median_list.add_command(label = "seating type", command = lambda: 
                        d1.median_score("SEATING TYPE"))
median_list.add_command(label = "zip code", command = lambda: 
                        d1.median_score("FACILITY ZIP"))

# Create sub menu for mode
mode_list.add_command(label = "seating type", command = lambda: 
                      d1.mode_score("SEATING TYPE"))
mode_list.add_command(label = "zip code", command = lambda: 
                      d1.mode_score("FACILITY ZIP"))

# Create sub menu for graphs. When the user clicks the menu, it triggers the
# function call to the respective functions that run the analytics of the data
# and visualize the results in a graph
graph_items.add_command(label = "Establishment/violation", command = lambda: 
                        d1.count_establishment_per_violation())
graph_items.add_command(label = "Violation/establishment/zipcode", command = 
                        lambda: d1.violations_per_establishment_per_zipcode())

# Create button widgets in the files frame in the main window. Each event, 
# triggers the target functions to upload the respective files into the app, clean 
# the data, display the data and save to the database.
button1 = Button(frame_files, text = "Upload and clean Inspections file", bg =
                "#8b0000", fg = "white", 
                 command = lambda: d1.load_inspections())
button1.place(rely = 0.45, relx = 0.10)
    
button2 = Button(frame_files, text = "Upload and clean violations file", bg =
                 "#580000", fg = "white", 
                 command = lambda: d1.load_violations())
button2.place(rely = 0.45, relx = 0.60)
     
    
def main():

    # Enter the event loop, the application constantly listens for events. 
    # Lets the widgets receive and react to the events.
    root.mainloop()
                   
   
if __name__ == "__main__":
  main()
