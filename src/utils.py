from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import QgsMessageBar

#	
# Utility funcions	
#
def setDialog(p_dialog):
    
    global _dialog
    _dialog = p_dialog
 
         
def setInterface(p_iface):
    
    global _iface, MSG_DURATION
    _iface = p_iface
    MSG_DURATION = 5        
 
    
def isFirstTime():
    
    global first
    if not 'first' in globals():
        first = True
    else:    
        first = False
    return first


def setCursor(p_cursor):
    
    global cursor
    cursor = p_cursor


def fillComboBox(elem, sql):
    
    elem.clear()	
    elem.addItem("")	
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        elem.addItem(row[0])	


def setSelectedItem(combo, sql):
    
    cursor.execute(sql)
    row = cursor.fetchone()
    if not row:
        return				
    elem = _dialog.findChild(QComboBox, combo)
    if elem:
        index = elem.findText(row[0])
        elem.setCurrentIndex(index);		


def getSelectedItem(param_elem):
    
    elem = _dialog.findChild(QComboBox, param_elem)
    if not elem.currentText():
        elem_text = "null"
    else:
        elem_text = "'"+elem.currentText()+"'"	
    elem_text = param_elem+"="+elem_text
    return elem_text	


def getSelectedItem2(param_elem):
    
    elem = _dialog.findChild(QComboBox, param_elem)
    if not elem.currentText():
        elem_text = "null"
    else:
        elem_text = "'"+elem.currentText()+"'"	
    return elem_text	


def getValue(param_elem):
    
    elem = _dialog.findChild(QLineEdit, param_elem)
    if elem:	
        if elem.text():
            elem_text = param_elem + " = "+elem.text().replace(",", ".")		      
        else:
            elem_text = param_elem + " = null"
    else:
        elem_text = param_elem + " = null"
    return elem_text


def getValue2(param_elem):
    
    elem = _dialog.findChild(QLineEdit, param_elem)
    if elem:	
        if elem.text():
            elem_text = elem.text().replace(",", ".")		      
        else:
            elem_text = "null"
    else:
        elem_text = "null"
    return elem_text


def getStringValue(param_elem):
    
    elem = _dialog.findChild(QLineEdit, param_elem)
    if elem:	
        if (not elem.text() or elem.text().lower() == "null"):
            elem_text = param_elem + " = null"    
        else:
            elem_text = param_elem + " = '"+elem.text().replace("'", "''")+"'"
    else:
        elem = _dialog.findChild(QTextEdit, param_elem)	
        if elem:	
            if (not elem.toPlainText() or elem.toPlainText().lower() == "null"):  
                elem_text = param_elem + " = null"    
            else:
                elem_text = param_elem + " = '"+elem.toPlainText().replace("'", "''")+"'"
        else:				
            elem_text = param_elem + " = null"
    return elem_text


def getStringValue2(param_elem):
    
    elem = _dialog.findChild(QLineEdit, param_elem)
    if elem:	
        if (not elem.text() or elem.text().lower() == "null"):
            elem_text = "null"
        else:
            elem_text = "'"+elem.text().replace("'", "''")+"'"
    else:
        elem = _dialog.findChild(QTextEdit, param_elem)	
        if elem:	
            if (not elem.toPlainText() or elem.toPlainText().lower() == "null"):                
                elem_text = "null"    
            else:
                elem_text = "'"+elem.toPlainText().replace("'", "''")+"'"
        else:				
            elem_text = "null"
    return elem_text	


def isNull(param_elem):
    
    elem = _dialog.findChild(QLineEdit, param_elem)
    empty = True	
    if elem:	
        if elem.text():
            empty = False
    return empty	


def showInfo(text, duration = None):
    
    if duration is None:
        _iface.messageBar().pushMessage("", text, QgsMessageBar.INFO, MSG_DURATION)  
    else:
        _iface.messageBar().pushMessage("", text, QgsMessageBar.INFO, duration)              
    
def showWarning(text, duration = None):
    
    if duration is None:
        _iface.messageBar().pushMessage("", text, QgsMessageBar.WARNING, MSG_DURATION)  
    else:
        _iface.messageBar().pushMessage("", text, QgsMessageBar.WARNING, duration)   


