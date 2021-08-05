# encoding: utf-8

###########################################################################################################
#
#
#	Palette Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Palette
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc, math
from GlyphsApp import *
from GlyphsApp.plugins import *
from AppKit import NSAffineTransform, NSAffineTransformStruct, NSUnionRect, NSMidX, NSMidY

def leftEdge(shape):
	return shape.bounds.origin.x
	
def horizontalCenter(shape):
	return shape.bounds.origin.x + shape.bounds.size.width/2

def rightEdge(shape):
	return shape.bounds.origin.x + shape.bounds.size.width

def bottomEdge(shape):
	return shape.bounds.origin.y

def verticalCenter(shape):
	return shape.bounds.origin.y + shape.bounds.size.height/2

def topEdge(shape):
	return shape.bounds.origin.y + shape.bounds.size.height

def shapeWidth(shape):
	if isinstance(shape, NSRect):
		return shape.size.width
	return shape.bounds.size.width

def shapeHeight(shape):
	if isinstance(shape, NSRect):
		return shape.size.height
	return shape.bounds.size.height

def transformationForMove(x=0.0, y=0.0):
	myTransform = NSAffineTransform.transform()
	myTransform.translateXBy_yBy_(x,y)
	return myTransform.transformStruct()



class Distribute (PalettePlugin):
	dialog = objc.IBOutlet()
	buttonDistributeTopEdges = objc.IBOutlet()
	buttonDistributeBottomEdges = objc.IBOutlet()
	buttonDistributeLeftEdges = objc.IBOutlet()
	buttonDistributeRightEdges = objc.IBOutlet()
	buttonDistributeCentersH = objc.IBOutlet()
	buttonDistributeCentersV = objc.IBOutlet()
	buttonDistributeGapsH = objc.IBOutlet()
	buttonDistributeGapsV = objc.IBOutlet()

	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({
			'en': 'Distribute',
			'de': 'Verteilen',
			'fr': 'Répartir',
			'es': 'Distribuir',
			'pt': 'Distribuir',
			'cs': 'Rozložit',
			})
		
		# Load .nib dialog (without .extension)
		self.loadNib('IBdialog', __file__)

	@objc.python_method
	def selectedObjects(self):
		selection = []
		# font = self.windowController().document().font
		tab = self.windowController().activeEditViewController()
		if tab:
			layer = tab.activeLayer()
			if layer:
				for selectedItem in layer.selection:
					if selectedItem in layer.shapes:
						selection.append(selectedItem)
					elif selectedItem.parent in layer.shapes:
						# partially selected path:
						parentItem = selectedItem.parent
						if not parentItem in selection:
							selection.append(parentItem)
		return selection

	@objc.python_method
	def distribute(self, distributePos=leftEdge, vertically=False):
		selectedObjects = self.selectedObjects()
		if selectedObjects:
			sortedShapes = sorted( selectedObjects, key = lambda shape: distributePos(shape) )
			firstPos = distributePos(sortedShapes[0])
			lastPos = distributePos(sortedShapes[-1])
			totalSpan = lastPos - firstPos
			shapeCount = len(sortedShapes)
			displacement = totalSpan/(shapeCount-1)
			for i, shape in enumerate(sortedShapes):
				if i>0 and i<(shapeCount-1): # do not need to move edge shapes
					currentAbsolutePos = distributePos(shape)
					newRelativePos = i*displacement
					move = firstPos+newRelativePos - currentAbsolutePos
					if vertically:
						movement = transformationForMove(y=move)
					else:
						movement = transformationForMove(x=move)
					shape.applyTransform( movement )

	@objc.IBAction
	def distributeBottomEdges_(self, sender):
		self.distribute(distributePos=bottomEdge, vertically=True)
	
	@objc.IBAction
	def distributeTopEdges_(self, sender):
		self.distribute(distributePos=topEdge, vertically=True)
	
	@objc.IBAction
	def distributeLeftEdges_(self, sender):
		self.distribute(distributePos=leftEdge, vertically=False)
	
	@objc.IBAction
	def distributeRightEdges_(self, sender):
		self.distribute(distributePos=rightEdge, vertically=False)
	
	@objc.IBAction
	def distributeCentersV_(self, sender):
		self.distribute(distributePos=verticalCenter, vertically=True)
	
	@objc.IBAction
	def distributeCentersH_(self, sender):
		self.distribute(distributePos=horizontalCenter, vertically=False)
	
	@objc.python_method
	def distributeGaps(self, widthOrHeight=shapeWidth, verticalDistribution=False):
		selectedObjects = self.selectedObjects()
		if selectedObjects:
			sortedShapes = sorted( 
				selectedObjects, 
				key = lambda shape: NSMidY(shape.bounds) if verticalDistribution else NSMidX(shape.bounds)
				)
				
			encompassingRect = sortedShapes[0].bounds.copy()
			totalWidthOrHeight = 0
			for shape in sortedShapes:
				encompassingRect = NSUnionRect(encompassingRect, shape.bounds)
				totalWidthOrHeight += widthOrHeight(shape)
			
			shapeCount = len(sortedShapes)
			gapCount = shapeCount-1
			encompassingWidthOrHeight = widthOrHeight(encompassingRect)
			totalGaps = encompassingWidthOrHeight - totalWidthOrHeight
			newGap = totalGaps/gapCount
			
			for i, shape in enumerate(sortedShapes):
				if i>0 and i<(shapeCount-1): # do not need to move edge shapes
					previousShape = sortedShapes[i-1]
					previousShapeEdge = topEdge(previousShape) if verticalDistribution else rightEdge(previousShape)
					shapeEdge = bottomEdge(shape) if verticalDistribution else leftEdge(shape)
					currentGap = shapeEdge - previousShapeEdge
					move = newGap - currentGap
					if verticalDistribution:
						movement = transformationForMove(y=move)
					else:
						movement = transformationForMove(x=move)
					shape.applyTransform( movement )
	
	@objc.IBAction
	def distributeGapsV_(self, sender):
		self.distributeGaps(widthOrHeight=shapeHeight, verticalDistribution=True)
	
	@objc.IBAction
	def distributeGapsH_(self, sender):
		self.distributeGaps(widthOrHeight=shapeWidth, verticalDistribution=False)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
