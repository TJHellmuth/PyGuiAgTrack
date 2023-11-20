import typing
import random
import os

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QComboBox,
    QListView,
    QMessageBox,
)
from PyQt6 import QtCore, QtGui

class FontendModel(QtCore.QAbstractListModel):
    def __init__(self, logic=None,selector=lambda a:a,action=lambda a,b:a,  name="debugg information"):
        super().__init__()
        self.logic = logic
        self.debug_name = name
        self.selector = selector
        self.removeAction = action
        script_dir = os.path.dirname(__file__)
        self.tick = QtGui.QImage(os.path.join(script_dir, 'tick.png'))
        self.untick = QtGui.QImage(os.path.join(script_dir, 'untick.png'))

    def select_elemets(self):
        return self.selector(self.logic.students['Students'], self.logic.select_ex)

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
        sup_flag = super().flags(index)
        #if (index.isValid() and index.model() == self):
        if (index.isValid()):
            return sup_flag  | QtCore.Qt.ItemFlag.ItemIsDragEnabled
        else:
            return sup_flag | QtCore.Qt.ItemFlag.ItemIsDropEnabled

    def supportedDropActions(self) -> QtCore.Qt.DropAction:
        return QtCore.Qt.DropAction.MoveAction
        #Qt.DropAction.TargetMoveAction

    def setData(self, index: QtCore.QModelIndex, value: typing.Any, role: int = ...) -> bool:
        print("setData")
        return True

    def insertRows(self, row: int, count: int, parent: QtCore.QModelIndex = ...) -> bool:
        print(f"insertRows {row=} {count=}")
        self.beginInsertRows(parent,row,row)
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QtCore.QModelIndex = ...) -> bool:
        print(f"removeRows {row=} {count=}")
        self.beginRemoveRows(parent, row,row)
        students_str = [st for st in self.select_elemets()]
        self.removeAction(students_str[row]['solved_ex'], self.logic.select_ex)
        self.endRemoveRows()
        return True

    def data(self, index: QtCore.QModelIndex, role: int) -> typing.Any:
        students=self.select_elemets()
        st = students[index.row()]
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            points = self.logic.query_points(st['solved_ex'])
            text = f"{st['name']} (Punkte: {points})"
            return text
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            if  self.logic.select_ex in  st['presented_ex'] :
                return self.tick
            else:
                return self.untick
    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        return len(self.select_elemets())

def select_submitted_students(stud_list, selected_ex) -> list:
    return list (filter(lambda x: selected_ex in x['solved_ex'], stud_list))
def select_not_submitted_students(stud_list, selected_ex) -> list:
    return list (filter(lambda x: not selected_ex in x['solved_ex'], stud_list))

class ComboModel(QtCore.QAbstractListModel):
    def __init__(self, logic=None, name="debugg information"):
        super().__init__()
        self.logic = logic
        self.debug_name = name
        self.exercise = [ex for ex in self.logic.exersises["Exercise"]]

    def data(self, index: QtCore.QModelIndex, role: int) -> typing.Any:
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            ex_str = [f"{ex['name']} (Punkte {ex['points']}) - {ex['date']}" for ex in self.exercise ]
            text = ex_str[index.row()]
            return text

    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        return len(self.logic.exersises["Exercise"])

class View(QListView):
    def __init__(self, name=""):
        super().__init__()
        self.name = name

    def dropEvent(self, e: typing.Optional[QtGui.QDropEvent]) -> None:
        if (e.source() != self):
            # only accept drops into different view
            super().dropEvent(e)

class Window(QWidget):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.model_not_submitted = FontendModel(logic=logic, selector=select_not_submitted_students, action=lambda a,b: a.append(b), name="not submitted" )
        self.model_submitted = FontendModel(logic=logic, selector=select_submitted_students, action=lambda a,b: a.remove(b), name="submitted")
        self.setWindowTitle(f"Abgaben Track : {logic.basedir}")
        # Create a QHBoxLayout instance
        layout = QHBoxLayout()
        # Student list
        layout_stud_list = QVBoxLayout()
        layout_submitted = QVBoxLayout()
        layout.addLayout(layout_stud_list)
        layout.addLayout(layout_submitted)

        # Add widgets to the layout
        students_list_view = View("studenten_list_view")
        students_list_view.setModel(self.model_not_submitted)
        students_list_view.setSelectionMode(QListView.SelectionMode.SingleSelection)
        students_list_view.setDragEnabled(True)
        students_list_view.setAcceptDrops(True)
        students_list_view.setDropIndicatorShown(True)
        layout_stud_list.addWidget(students_list_view)

        ## Submitted List
        ex_select = QComboBox()
        self.combo_model = ComboModel(logic)
        ex_select.setModel(self.combo_model)
        ex_select.currentIndexChanged.connect(self.idx_change)
        ex_select.currentIndexChanged.emit(ex_select.currentIndex())
        layout_submitted.addWidget(ex_select)

        self.submissions_view = View("submit_list_view")
        self.submissions_view.setModel(self.model_submitted)
        self.submissions_view.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.submissions_view.setDragEnabled(True)
        self.submissions_view.setAcceptDrops(True)
        self.submissions_view.setDropIndicatorShown(True)
        layout_submitted.addWidget(self.submissions_view)

        store_submission = QPushButton("Save")
        store_submission.clicked.connect(self.store_submissions)
        layout_submitted.addWidget(store_submission)
        choose_button = QPushButton("Chose")
        choose_button.clicked.connect(self.choose)
        layout_submitted.addWidget(choose_button)
        present_button = QPushButton("Presented")
        present_button.clicked.connect(self.present_toggle)
        layout_submitted.addWidget(present_button)

        self.setLayout(layout)
        print(self.children())

    def closeEvent(self, event: typing.Optional[QtGui.QCloseEvent]) -> None:
        stored = self.logic.getStudents()
        if (stored == self.logic.students) :
            event.accept()
            return

        msgBox = QMessageBox()
        msgBox.setText("The document has been modified.")
        msgBox.setInformativeText("Do you want to save your changes?")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        ret = msgBox.exec()
        if ret == QMessageBox.StandardButton.Save:
            print("saving ... ")
            self.store_submissions()
            event.accept()
        elif ret == QMessageBox.StandardButton.Discard:
            event.accept()
        elif ret == QMessageBox.StandardButton.Cancel:
            event.ignore()

    def store_submissions(self):
        self.logic.writeStudents()

    def idx_change(self, idx):
        print(f"{idx=}  old:{self.logic.select_ex=}  new:{self.combo_model.exercise[idx]['id']=}")
        idx_end_not = self.model_not_submitted.index(self.model_not_submitted.rowCount(self.model_not_submitted.parent()) - 1)
        idx_end= self.model_submitted.index(self.model_submitted.rowCount(self.model_submitted.parent()) - 1)
        self.logic.select_ex = self.combo_model.exercise[idx]["id"]
        # refresh all views
        self.model_not_submitted.dataChanged.emit(self.model_not_submitted.index(0), idx_end_not, [QtCore.Qt.ItemDataRole.DisplayRole])
        self.model_submitted.dataChanged.emit(self.model_submitted.index(0), idx_end, [QtCore.Qt.ItemDataRole.DisplayRole])

    def choose(self):
        st_list = self.model_submitted.select_elemets()
        weights = [1/(1+len(st['presented_ex']))  for st in st_list]
        selected_st = random.choices(st_list, weights=weights)[0]
        print(f"selected {selected_st=}")

        msgBox = QMessageBox()
        msgBox.setText(f"{selected_st['name']}")
        msgBox.exec()


    def present_toggle(self):
        idx_sel = self.submissions_view.selectedIndexes()
        print(idx_sel)
        if (len(idx_sel) == 0 ):
            print ("please select an emement of the list")
            return
        idx_qt = [i for i in idx_sel][0]
        idx = idx_qt.row()
        st_list = self.model_submitted.select_elemets()
        if self.logic.select_ex in st_list[idx]['presented_ex']:
            st_list[idx]['presented_ex'].remove(self.logic.select_ex)
        else:
            st_list[idx]['presented_ex'].append(self.logic.select_ex)

        self.model_submitted.dataChanged.emit(idx_qt, idx_qt, [QtCore.Qt.ItemDataRole.DecorationRole])

