import random
import Utils
import Constants
import math

#TODO сделать так, чтобы на объекты классов моно было применить функцию len()

class Data:
    def __init__(self, columns):
        self._columns = columns
        self._rows = []
        for i, element in enumerate(self._columns[0]): #i - это строка
            rowArray = []
            for j in range (0, len(self._columns)):        #j - это колонка
                rowArray.append(self._columns[j][i])
            self._rows.append(Row(i, rowArray))

        self._rowCount = len(self._rows)
        self._columnCount = len(self._columns)
        self._columnNames = []
        for column in self._columns:
            self._columnNames.append(column.getName())

    def getRows(self):
        return self._rows

    def rowCount(self):
        return self._rowCount

    def getColumns(self):
        return self._columns

    def columnCount(self):
        return self._columnCount

    def getColumnNames(self):
        return self._columnNames

    def getSignificantColumns(self):
        significantcolumns = []
        for column in self._columns:
            if column.checkSignificance():
                significantcolumns.append(column)
        return significantcolumns

    def significantColumnCount(self):
        return len(self.getSignificantColumns())

    def getSignificantColumnNames(self):
        significantColumnNames = []
        for column in self.getSignificantColumns():
            significantColumnNames.append(column.getName())
        return significantColumnNames

    def getNameOfColumn(self, columnindex):
        return self._columnNames[columnindex]

    def getRowsByIndexSet(self, indexSet):
        rows = []
        for i in indexSet:
            rows.append(self._rows[i])
        return rows

    def getDummyCluster(self, clusters):
        busyIndexes = set()
        allIndexes = set()
        for i in range(0, self.rowCount()):
            allIndexes.add(i)
        for cluster in clusters:
            busyIndexes = busyIndexes | cluster.getIndexSet()
        unbusyIndexes = allIndexes - busyIndexes
        rows = self.getRowsByIndexSet(unbusyIndexes)
        dummyCluster = Cluster(rows)
        dummyCluster.setColor(Constants.DEFAULT_POINT_COLOR)
        dummyCluster.setShapeKey('circle')
        dummyCluster.setName('dummyCluster')
        return dummyCluster

class Cluster:
    def __init__(self, rows = []):
        self._rows = rows
        self._name = "nameless cluster"
        colorRange = Constants.DEFAULT_COLOR_SET
        self._color = random.choice(colorRange)
        self._shapeKey = "circle"
        self._hidden = False

    def setHidden(self, value):
        self._hidden = value
        for row in self._rows:
            row.setHidden(value)

    def getRowByRowOriginalIndex(self, index):
        for row in self._rows:
            if row.getIndex() == index:
                return row
        return None

    def __getitem__(self, index):
        return self._rows[index]

    def __setitem__(self, index, value):
        self._rows[index] = value

    def __delitem__(self, index):
        del self._rows[index]

    def isHidden(self):
        return self._hidden

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getRows(self):
        return self._rows

    def setRows(self, rows):
        self._rows = rows

    def getColor(self):
        return self._color

    def setColor(self, color):
        self._color = color

    def getShapeKey(self):
        return self._shapeKey

    def getShape(self):
        return Utils.getFlippedMarkerDictionary().get(self.getShapeKey())

    def setShapeKey(self, shapeKey):
        self._shapeKey = shapeKey

    def getIndexSet(self):
        indexSet = set()
        for row in self._rows:
            indexSet.add(row.getIndex())
        return indexSet

    def getIndexList(self):
        indexes = []
        for row in self._rows:
            indexes.append(row.getIndex())
        return indexes

    def getSize(self):
        return len(self._rows)

    def draw2DProjection(self, axes, xindex, yindex):
        points = []
        xData = []
        yData = []
        for row in self._rows:
            point = row.getProjection(xindex, yindex)
            points.append(point)
            if not point.isHidden():
                xData.append(point.getX())
                yData.append(point.getY())
        axes.plot(xData, yData,
                  linestyle="None",
                  marker=self.getShape(),
                  color=self.getColor(),
                  markersize = Constants.DEFAULT_MARKER_SIZE_BIG)

    def evaluateMassCenter(self):
        rowsAmount = len(self._rows)
        if rowsAmount > 0:
            massCenterDataArray = [0] * self._rows[0].getLength()
            for row in self._rows:
                for i in range(0, row.getLength()):
                    massCenterDataArray[i] += row[i]
            massCenterDataArray[:] = [element / rowsAmount for element in massCenterDataArray]
            return Row(None, massCenterDataArray)
        else:
            return None

class Row:
    def __init__(self, index, dataArray):
        self._index = index
        self._dataArray = dataArray
        self._hidden = False

    def __getitem__(self, index):
        return self._dataArray[index]

    def __setitem__(self, index, value):
        self._dataArray[index] = value

    def __delitem__(self, index):
        del self._dataArray[index]

    def getIndex(self):
        return self._index

    def setIndex(self, index):
        self.index = index

    def getDataArray(self):
        return self._dataArray

    def setDataArray(self, dataArray):
        self._dataArray = dataArray

    def setHidden(self, value):
        self._hidden = value

    def isHidden(self):
        return self._hidden

    def getLength(self):
        if self._dataArray is not None:
            return len(self._dataArray)
        else:
            return None

    def getProjection(self, i, j):
        x = self._dataArray[i]
        y = self._dataArray[j]
        point = Point(x, y, self._index)
        point.setHidden(self._hidden)
        return point

    def distanceTo(self, anotherRow):
        anotherDataArray = anotherRow.getDataArray()
        sumOfSquares = 0
        for i, element in enumerate(self._dataArray): #TODO сделать коэффициент значимости
            sumOfSquares += (element - anotherDataArray[i]) * (element - anotherDataArray[i])
        return math.sqrt(sumOfSquares)

    def manhattanDistanceTo(self, anotherRow):
        anotherDataArray = anotherRow.getDataArray()
        sum = 0
        for i, element in enumerate(self._dataArray):  # TODO сделать коэффициент значимости
            sum += abs(element - anotherDataArray[i])
        return sum

class Column:
    def __init__(self, name, data, index):
        self._name = name
        self._data = data
        self._index = index
        self._isSignificant = True
        self._averagevalue = 0 #sum(self._data)/len(self._data)
        self._standartderivation = 0
        for element in self._data:
            self._standartderivation += 0 #(self._averagevalue - element) * (self._averagevalue - element)
        self._standartderivation = math.sqrt(self._standartderivation / len(self._data))
        self._weight = 1

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __delitem__(self, index):
        del self._data[index]

    def getName(self):
        return self._name

    def getData(self):
        return self._data

    def getIndex(self):
        return self._index

    def setSignificance(self, boolvalue):
        self._isSignificant = boolvalue

    def checkSignificance(self):
        return self._isSignificant

    def getAverageValue(self):
        return self._averagevalue

    def getStandartDerivation(self):
        return self._standartderivation

    def setWeight(self, value):
        self._weight = value

    def getWeight(self):
        return self._weight

class Point:
    def __init__(self, x, y, index):
        self._x = x
        self._y = y
        self._index = index
        self._hidden = False

    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def getIndex(self):
        return self._index

    def setHidden(self, value):
        self._hidden = value

    def isHidden(self):
        return self._hidden



