﻿from PyQt4.QtCore import *
from PyQt4.QtGui import *
from utils import *
from datetime import datetime
import time
import sqlite3
import os.path
from photo_dialog import PhotoDialog


def formOpen(dialog,layerid,featureid):

    global _dialog, id, cbo_marc_legal, lbl_info
    global db_file, photo_folder

    # Set global variables	
    _dialog = dialog
    setDialog(dialog)	
    id = _dialog.findChild(QLineEdit, "id")		
    cbo_marc_legal = _dialog.findChild(QComboBox, "marc_legal_id")	
    lbl_info = _dialog.findChild(QLabel, "lbl_info")		
    current_path = os.path.dirname(os.path.abspath(__file__))
    
    # Get current path
    db_file = current_path+"/cens_2013.sqlite"	
    photo_folder = current_path+"/fotos/"		

    # Wire up our own signals
    cbo_marc_legal.currentIndexChanged.connect(marcLegalChanged)		
    _dialog.findChild(QPushButton, "previous").clicked.connect(previousRecord)	
    _dialog.findChild(QPushButton, "next").clicked.connect(nextRecord)	
    _dialog.findChild(QPushButton, "create_act").clicked.connect(createActivity)	
    _dialog.findChild(QPushButton, "duplicate_act").clicked.connect(duplicateActivity)		
    _dialog.findChild(QPushButton, "save_act").clicked.connect(saveClicked)	
    _dialog.findChild(QPushButton, "del_act").clicked.connect(deleteActivity)	
    _dialog.findChild(QPushButton, "photo_act").clicked.connect(viewPhoto)		
    _dialog.findChild(QPushButton, "close").clicked.connect(_dialog.reject)	
    
    # Connect to Database
    connectDb()

    # Tab 'activities': Load related combos 
    loadActivityCombos()

    # Get number of activitites related to current emplacament
    updateTotals()	

    # Disable and set invisible some controls		
    disableControls()


# Connect to Database	
def connectDb():
    
    global conn, cursor
    conn = sqlite3.connect(db_file)
    #conn.text_factory = sqlite3.OptimizedUnicode	
    cursor = conn.cursor()	
    setCursor(cursor)		


# Disable and set invisible some controls	
def disableControls():

    _dialog.findChild(QLineEdit, "id").setEnabled(False)
    _dialog.findChild(QLineEdit, "act_id").setEnabled(False)	


# Load combos from domain tables	
def loadActivityCombos():

    sql = "SELECT id FROM ta_estat_legal ORDER BY id"
    fillComboBox(_dialog.findChild(QComboBox, "estat_legal_id"), sql)	
    sql = "SELECT id FROM ta_tipus_act ORDER BY id"
    fillComboBox(_dialog.findChild(QComboBox, "tipus_act_id"), sql)		
    sql = "SELECT id FROM ta_marc_legal ORDER BY id"
    fillComboBox(_dialog.findChild(QComboBox, "marc_legal_id"), sql)	
    sql = "SELECT id FROM ta_clas_legal ORDER BY id"
    fillComboBox(_dialog.findChild(QComboBox, "clas_legal_id"), sql)	


def updateTotals():

    global row_total, row_cur
    row_cur = 0
    row_total = getTotal()	
    if (row_total > 0):
        row_cur = 1	
    #lbl_info.setText("Activitat "+str(row_cur)+" de "+str(row_total)) 
    enable_previous = (row_cur > 1)
    enable_next = (row_total > row_cur)      
    _dialog.findChild(QPushButton, "previous").setEnabled(enable_previous) 
    _dialog.findChild(QPushButton, "next").setEnabled(enable_next)     
    loadActivity()    
    

def previousRecord():

    global row_cur
    row_cur = row_cur - 1;		
    if (row_cur <= 1):
        _dialog.findChild(QPushButton, "previous").setEnabled(False)	
    _dialog.findChild(QPushButton, "next").setEnabled(True)		
    saveActivity(False)	
    loadActivity()		


def nextRecord():

    global row_cur
    row_cur = row_cur + 1;	
    if (row_cur >= row_total):
        _dialog.findChild(QPushButton, "next").setEnabled(False)	
    _dialog.findChild(QPushButton, "previous").setEnabled(True)			
    saveActivity(False)		
    loadActivity()		


# Update combo 'clas_legal_id', depending selected 'marc_legal_id'
def marcLegalChanged():

    marc_legal = cbo_marc_legal.currentText()
    if not marc_legal:
        sql = "SELECT DISTINCT(clas_id) FROM ta_marc_x_clas ORDER BY clas_id"
    else:
        # Get only clas_legal records related to selected marc_legal. Table: ta_marc_x_clas
        sql = "SELECT clas_id FROM ta_marc_x_clas WHERE marc_id = '"+marc_legal+"' ORDER BY clas_id"
    #print sql		
    fillComboBox(_dialog.findChild(QComboBox, "clas_legal_id"), sql)	


def getTotal():

    sql = "SELECT COUNT(*) FROM activitat WHERE emplacament_id = '"+id.text()+"'"	
    cursor.execute(sql)
    row = cursor.fetchone()	
    row_total = row[0]
    return row_total	


# Load data related to current Activity from Database	
def loadActivity():

    global rows, iterator

    # Dades generals activitat
    sql = "SELECT id, nif, rao_social, nom_comercial, descripcio, nom_contacte, telefon, mail, superficie, actual"
    # Marc legal
    sql+= ", exp_relacionats, num_llicencia, data_llicencia, data_baixa, data_control_inicial, data_control_periodic, estat_legal_id, tipus_act_id, marc_legal_id, clas_legal_id, codi_legal, observacions_act, num_exp"	
    sql+= " FROM activitat WHERE emplacament_id = '"+id.text()+"' ORDER BY id DESC"
    sql+= " LIMIT 1 OFFSET "+str(row_cur-1)
    cursor.execute(sql)
    #print sql	
    lbl_info.setText("Activitat "+str(row_cur)+" de "+str(row_total))	
    row = cursor.fetchone()		
    if row:	
        setWidgetsActivity(row)		
        checkPhoto()		   


def checkPhoto():

    act_id = _dialog.findChild(QLineEdit, "act_id")	
    path = photo_folder+act_id.text()+".jpg"
    exists = os.path.isfile(path)
    _dialog.findChild(QPushButton, "photo_act").setEnabled(exists)


def setWidgetsActivity(row):

    setField(row, 0, "act_id")
    setField(row, 1, "nif")	
    setField(row, 2, "rao_social")
    setField(row, 3, "nom_comercial")
    setTextEdit(row, 4, "descripcio")
    setField(row, 5, "nom_contacte")
    setField(row, 6, "telefon")
    setField(row, 7, "mail")	
    setField(row, 8, "superficie")	
    #setField(row, 9, "actual")	
    setField(row, 10, "exp_relacionats")	
    #setField(row, 11, "num_llicencia")			
    setDate(row, 12, "data_llicencia")
    setDate(row, 13, "data_baixa")
    setDate(row, 14, "data_control_inicial")
    setDate(row, 15, "data_control_periodic")	
    setCombo(row, 16, "estat_legal_id")	
    setCombo(row, 17, "tipus_act_id")
    setCombo(row, 18, "marc_legal_id")
    setCombo(row, 19, "clas_legal_id")
    setField(row, 20, "codi_legal")
    setTextEdit(row, 21, "observacions_act")
    setField(row, 22, "num_exp")		

    chk_actual = _dialog.findChild(QCheckBox, "actual")	
    if row[9]==-1:
        chk_actual.setChecked(True);
    else:
        chk_actual.setChecked(False);	


def setTextEdit(row, index, field):
    aux = _dialog.findChild(QTextEdit, field)   
    if not aux:
        print "field not found: " + field	
        return	
    value = unicode(row[index])
    if value == 'None':	
        aux.setText("") 		
    else:
        aux.setText(value) 		

def setField(row, index, field):
    aux = _dialog.findChild(QLineEdit, field)   
    if not aux:
        print "field not found: " + field	
        return	
    value = unicode(row[index])
    if value == 'None':	
        aux.setText("") 		
    else:
        aux.setText(value) 			


def setCombo(row, index, field):
    aux = _dialog.findChild(QComboBox, field)   
    if not aux:
        print "combo not found: " + field	
        return	
    index = aux.findText(row[index])		
    aux.setCurrentIndex(index);		


def setDate(row, index, field):
    aux = _dialog.findChild(QDateEdit, field)   
    if not aux:
        print "date not found: " + field	
        return	
    if row[index]:	
        date = datetime.strptime(row[index], "%Y-%m-%d")			
    else:
        date = datetime.strptime("1900-01-01", "%Y-%m-%d")							
    aux.setDate(date);		


def createActivity():

    lbl_info.setText("Creant activitat...")	
    sql = "SELECT 1 + (SELECT id FROM activitat ORDER BY id DESC LIMIT 1)"
    cursor.execute(sql)
    row = cursor.fetchone()		
    _dialog.findChild(QLineEdit, "act_id").setText(str(row[0]))
    _dialog.findChild(QLineEdit, "new_emp_id").setText("")
    _dialog.findChild(QLineEdit, "new_emp_id").setEnabled(False)   
    _dialog.findChild(QLineEdit, "nif").setText("")
    _dialog.findChild(QLineEdit, "rao_social").setText("")
    _dialog.findChild(QLineEdit, "nom_comercial").setText("")
    _dialog.findChild(QTextEdit, "descripcio").setText("")
    _dialog.findChild(QLineEdit, "nom_contacte").setText("")
    _dialog.findChild(QLineEdit, "telefon").setText("")
    _dialog.findChild(QLineEdit, "mail").setText("")
    _dialog.findChild(QLineEdit, "superficie").setText("")
    _dialog.findChild(QLineEdit, "exp_relacionats").setText("")
    _dialog.findChild(QLineEdit, "num_exp").setText("")
    _dialog.findChild(QLineEdit, "codi_legal").setText("")	
    _dialog.findChild(QTextEdit, "observacions_act").setText("")	
    _dialog.findChild(QComboBox, "estat_legal_id").setCurrentIndex(-1)
    _dialog.findChild(QComboBox, "tipus_act_id").setCurrentIndex(-1)
    _dialog.findChild(QComboBox, "marc_legal_id").setCurrentIndex(-1)
    _dialog.findChild(QComboBox, "clas_legal_id").setCurrentIndex(-1)

    # Get current date
    current_date = time.strftime("%Y-%m-%d")
    date = datetime.strptime(current_date, "%Y-%m-%d")
    _dialog.findChild(QDateEdit, "data_llicencia").setDate(date);	 
    _dialog.findChild(QDateEdit, "data_baixa").setDate(date);	 	
    _dialog.findChild(QDateEdit, "data_control_inicial").setDate(date);	    
    _dialog.findChild(QDateEdit, "data_control_periodic").setDate(date);	    	
    _dialog.findChild(QLineEdit, "num_exp").setText("")		


def duplicateActivity():

    lbl_info.setText("Duplicant activitat...")	
    sql = "SELECT 1 + (SELECT id FROM activitat ORDER BY id DESC LIMIT 1)"
    cursor.execute(sql)
    row = cursor.fetchone()		
    _dialog.findChild(QLineEdit, "act_id").setText(str(row[0]))


# Delete current activity
def deleteActivity():

    act_id = _dialog.findChild(QLineEdit, "act_id")	
    msgBox = QMessageBox()
    msgBox.setWindowTitle("Eliminar activitat")	
    msgBox.setText(u"Està segur que desitja esborrar aquesta activitat?")
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.Yes)
    resp = msgBox.exec_()
    if (resp == QMessageBox.Yes):
        sql = "DELETE FROM activitat WHERE id = "+act_id.text()	
        cursor.execute(sql)			
        conn.commit()		
        updateTotals()	


def saveClicked():
    saveActivity(True)


# Save data from Tab 'Activities' into Database
def saveActivity(update):
 
    act_id = _dialog.findChild(QLineEdit, "act_id")	
    dllic = _dialog.findChild(QDateEdit, "data_llicencia")	
    dllic_value = dllic.date().toString("yyyy-MM-dd")
    dllic_text = "data_llicencia = '"+dllic_value+"'"	
    dbaixa = _dialog.findChild(QDateEdit, "data_baixa")	
    dbaixa_value = dbaixa.date().toString("yyyy-MM-dd")
    dbaixa_text = "data_baixa = '"+dbaixa_value+"'"		
    dci = _dialog.findChild(QDateEdit, "data_control_inicial")	
    dci_value = dci.date().toString("yyyy-MM-dd")
    dci_text = "data_control_inicial = '"+dci_value+"'"	
    dcp = _dialog.findChild(QDateEdit, "data_control_periodic")	
    dcp_value = dcp.date().toString("yyyy-MM-dd")
    dcp_text = "data_control_periodic = '"+dcp_value+"'"	

    chk_actual = _dialog.findChild(QCheckBox, "actual")	
    actual_value = chk_actual.isChecked()
    if actual_value:	
        actual_value = -1	
    else:
        actual_value = 0
    actual_text = "actual = "+str(actual_value)

    #emplacament_text = "emplacament_id = null"	
    emplacament_value = "null"
    new_emp_id = _dialog.findChild(QLineEdit, "new_emp_id")
    new_emp_text = ""
    if new_emp_id.text():
        new_emp_value = "'"+new_emp_id.text()+"'"        
        new_emp_text = "emplacament_id = "+new_emp_value  
    new_emp_id.setEnabled(True) 
    new_emp_id.setText("")
    emp_id = _dialog.findChild(QLineEdit, "id")	
    if emp_id.text():
        emplacament_value = "'"+emp_id.text()+"'"		
        #emplacament_text = "emplacament_id = "+emplacament_value

    # Create SQL
    sql = "UPDATE activitat"
    sql+= " SET "+getStringValue("nif")+", "+getStringValue("rao_social")+", "+getStringValue("nom_comercial")+", "+getStringValue("descripcio")+", "+getStringValue("nom_contacte")+", "+getStringValue("telefon")+", "+getStringValue("mail")+", "+getStringValue("superficie")+", "+getStringValue("exp_relacionats")+", "+dllic_text+", "+dbaixa_text+", "+dci_text+", "+dcp_text
    sql+= ", "+getSelectedItem("estat_legal_id")+", "+getSelectedItem("tipus_act_id")+", "+getSelectedItem("marc_legal_id")+", "+getSelectedItem("clas_legal_id")+", "+getStringValue("codi_legal")+", "+getStringValue("observacions_act")+", "+getStringValue("num_exp")+", "+actual_text	
    if new_emp_text:
        sql+= ", "+new_emp_text
    sql+= " WHERE id = "+act_id.text()
    #print sql		
    cursor.execute(sql)
    if cursor.rowcount == 0:	
        sql = "INSERT INTO activitat (emplacament_id, nif, rao_social, nom_comercial, descripcio, nom_contacte, telefon, mail, superficie, exp_relacionats, data_llicencia, data_baixa, data_control_inicial, data_control_periodic, estat_legal_id, tipus_act_id, marc_legal_id, clas_legal_id, codi_legal, observacions_act, num_exp, actual)"
        sql+= " VALUES ("+emplacament_value+", "+getStringValue2("nif")+", "+getStringValue2("rao_social")+", "+getStringValue2("nom_comercial")+", "+getStringValue2("descripcio")+", "+getStringValue2("nom_contacte")+", "+getStringValue2("telefon")+", "+getStringValue2("mail")+", "+getStringValue2("superficie")+", "+getStringValue2("exp_relacionats")+", '"+dllic_value+"', '"+dbaixa_value+"', '"+dci_value+"', '"+dcp_value+"', "+getSelectedItem2("estat_legal_id")+", "+getSelectedItem2("tipus_act_id")+", "+getSelectedItem2("marc_legal_id")+", "+getSelectedItem2("clas_legal_id")+", "+getStringValue2("codi_legal")+", "+getStringValue2("observacions_act")+", "+getStringValue2("num_exp")+", "+str(actual_value)+")"			
        #print sql				
        cursor.execute(sql)		
    conn.commit()	

    if (update):	
        updateTotals()	


def viewPhoto():

    act_id = _dialog.findChild(QLineEdit, "act_id")	
    path = photo_folder+act_id.text()+".jpg"
    photo_dialog = PhotoDialog()
    photo_dialog.setPhoto(path)    	
    photo_dialog.exec_()	


def saveFeature():
    
    saveActivity(False)
    # Return the form as accepted to QGIS	
    _dialog.accept()