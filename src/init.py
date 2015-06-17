from PyQt4.QtCore import *
from PyQt4.QtGui import *
from utils import *
from datetime import datetime
import time
import sqlite3
import os.path
from photo_dialog import PhotoDialog


def formOpen(dialog,layerid,featureid):

    global _dialog, id, cbo_marc_legal, lbl_info
    global db_file, photo_folder, emp_updating
    global current_path

    # Set global variables	
    _dialog = dialog
    setDialog(dialog)	
    id = _dialog.findChild(QLineEdit, "id")		
    cbo_marc_legal = _dialog.findChild(QComboBox, "marc_legal_id")	
    lbl_info = _dialog.findChild(QLabel, "lbl_info")		
    current_path = os.path.dirname(os.path.abspath(__file__))
    
    # Enable modification of activities, only if location is already created
    if id.text():
        emp_updating = True    
    else:
        emp_updating = False
    
    # Get current path
    db_file = current_path+"/cens_2014.sqlite"	
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
    _dialog.findChild(QPushButton, "close").clicked.connect(closeForm)	
    
    # Connect to Database
    connectDb()

    # Tab 'activities': Load related combos 
    loadActivityCombos()

    # Get number of activitites related to current emplacament
    updateTotals()	

    # Disable and set invisible some controls		
    disableControls()
    _dialog.hideButtonBox()    	


# Connect to Database	
def connectDb():
    
    global conn, cursor
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()	
    setCursor(cursor)		


# Disable and set invisible some controls	
def disableControls():

    _dialog.findChild(QLineEdit, "id").setEnabled(False)
    _dialog.findChild(QLineEdit, "act_id").setEnabled(False)	
    _dialog.findChild(QGroupBox, "gb_activitat").setEnabled(emp_updating)       
    _dialog.findChild(QGroupBox, "gb_marc_legal").setEnabled(emp_updating)          
    _dialog.findChild(QPushButton, "create_act").setEnabled(emp_updating)      
    _dialog.findChild(QPushButton, "duplicate_act").setEnabled(emp_updating)   
    _dialog.findChild(QPushButton, "del_act").setEnabled(emp_updating)  
    _dialog.findChild(QPushButton, "photo_act").setEnabled(emp_updating)   
    _dialog.findChild(QPushButton, "report").setVisible(False)   


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
    
    aux = _dialog.findChild(QLineEdit, field)   
    if not aux:
        print "date not found: " + field	
        return	 
    value = unicode(row[index])    
    #print field + ": " + value      
    if value != 'null' and value != 'None' and value != '1900-01-01':   
        date_aux = datetime.strptime(row[index], "%Y-%m-%d")
        date_text = date_aux.strftime("%d/%m/%Y")
    else:
        date_text = ""    				     
    aux.setText(date_text);	
    
    
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
    _dialog.findChild(QLineEdit, "num_exp").setText("")            
    _dialog.findChild(QComboBox, "estat_legal_id").setCurrentIndex(-1)
    _dialog.findChild(QComboBox, "tipus_act_id").setCurrentIndex(-1)
    _dialog.findChild(QComboBox, "marc_legal_id").setCurrentIndex(-1)
    _dialog.findChild(QComboBox, "clas_legal_id").setCurrentIndex(-1)
    _dialog.findChild(QLineEdit, "data_llicencia").setText("")  	 
    _dialog.findChild(QLineEdit, "data_baixa").setText("")  	 	
    _dialog.findChild(QLineEdit, "data_control_inicial").setText("")  	    
    _dialog.findChild(QLineEdit, "data_control_periodic").setText("")  	    	


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


def manageDate(widget):

    try:    
        date_widget = _dialog.findChild(QLineEdit, widget)
        aux = date_widget.text().replace("-", "/") 
        if aux:   
            date_aux = datetime.strptime(aux, "%d/%m/%Y")
            value = date_aux.strftime("%Y-%m-%d")
            text = widget+"='"+value+"', "  
        else:
            value = "null"
            text = widget+"=null, "              
    except ValueError:
        value = "null"
        text = "" 
    return dict(value = value, text = text)


# Save data from Tab 'Activities' into Database
def saveActivity(update):
 
    act_id = _dialog.findChild(QLineEdit, "act_id")	
    if not act_id.text():
        return
    
    dllic = manageDate("data_llicencia")
    dbaixa = manageDate("data_baixa")
    dci = manageDate("data_control_inicial")
    dcp = manageDate("data_control_periodic")
    print dbaixa["text"]
        
    chk_actual = _dialog.findChild(QCheckBox, "actual")	
    actual_value = chk_actual.isChecked()
    if actual_value:	
        actual_value = -1	
    else:
        actual_value = 0
    actual_text = "actual = "+str(actual_value)
    data_modif_text = "data_modif = datetime('now')"

    emp_value = "null"
    new_emp_id = _dialog.findChild(QLineEdit, "new_emp_id")
    new_emp_text = ""
    if new_emp_id.text():
        new_emp_value = "'"+new_emp_id.text()+"'"        
        new_emp_text = "emplacament_id = "+new_emp_value  
    emp_id = _dialog.findChild(QLineEdit, "id")	
    if emp_id.text():
        emp_value = emp_id.text()		

    # Create SQL
    sql = "UPDATE activitat"
    sql+= " SET "+getStringValue("nif")+", "+getStringValue("rao_social")+", "+getStringValue("nom_comercial")+", "+getStringValue("descripcio")+", "+getStringValue("nom_contacte") 
    sql+= ", "+getStringValue("telefon")+", "+getStringValue("mail")+", "+getStringValue("superficie")+", "+getStringValue("exp_relacionats")+", "+dllic["text"]+dbaixa["text"]+dci["text"]+dcp["text"]
    sql+= getSelectedItem("estat_legal_id")+", "+getSelectedItem("tipus_act_id")+", "+getSelectedItem("marc_legal_id")+", "+getSelectedItem("clas_legal_id") 
    sql+= ", "+getStringValue("codi_legal")+", "+getStringValue("observacions_act")+", "+getStringValue("num_exp")+", "+actual_text+", "+data_modif_text
    # Update location?
    if new_emp_text:
        msgBox = QMessageBox()
        msgBox.setWindowTitle(u"Modificar emplaçament")    
        msgBox.setText(u"Està segur que desitja modificar l'emplaçament de l'activitat?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        resp = msgBox.exec_()
        if (resp == QMessageBox.Yes):        
            sql+= ", "+new_emp_text
    sql+= " WHERE id = "+act_id.text()		
    cursor.execute(sql)
    
    if cursor.rowcount == 0:	
        sql = "INSERT INTO activitat (emplacament_id, nif, rao_social, nom_comercial, descripcio, nom_contacte, telefon, mail, superficie, exp_relacionats," 
        sql+= " data_llicencia, data_baixa, data_control_inicial, data_control_periodic, estat_legal_id, tipus_act_id, marc_legal_id, clas_legal_id, codi_legal, observacions_act, num_exp, actual)"
        sql+= " VALUES ("+emp_value+", "+getStringValue2("nif")+", "+getStringValue2("rao_social")+", "+getStringValue2("nom_comercial")+", "+getStringValue2("descripcio")
        sql+= ", "+getStringValue2("nom_contacte")+", "+getStringValue2("telefon")+", "+getStringValue2("mail")+", "+getStringValue2("superficie")+", "+getStringValue2("exp_relacionats")
        sql+= ", '"+dllic["value"]+"', '"+dbaixa["value"]+"', '"+dci["value"]+"', '"+dcp["value"]+"', "+getSelectedItem2("estat_legal_id")+", "+getSelectedItem2("tipus_act_id")
        sql+= ", "+getSelectedItem2("marc_legal_id")+", "+getSelectedItem2("clas_legal_id")+", "+getStringValue2("codi_legal")+", "+getStringValue2("observacions_act")+", "+getStringValue2("num_exp")+", "+str(actual_value)+")"						
        cursor.execute(sql)		
    conn.commit()	

    new_emp_id.setEnabled(True) 
    new_emp_id.setText("")
    
    if (update):	
        updateTotals()	
    
    
def saveLocation():
    
    emp_id = _dialog.findChild(QLineEdit, "id")        
    sql = "UPDATE emplacament"
    sql+= " SET "+getStringValue("adress")+", "+getStringValue("refcat_all")+", "+getStringValue("titular")+", "+getStringValue("observacions")    
    sql+= " WHERE id = "+emp_id.text()       
    cursor.execute(sql)
    conn.commit()    


def viewPhoto():

    act_id = _dialog.findChild(QLineEdit, "act_id")	
    path = photo_folder+act_id.text()+".jpg"
    photo_dialog = PhotoDialog()
    photo_dialog.setPhoto(path)    	
    photo_dialog.exec_()	
     

def saveClicked():
    if emp_updating:
        saveLocation()
        saveActivity(True)
    else:
        _dialog.accept()        
    
    
def closeForm():
    _dialog.parent().setVisible(False)
    