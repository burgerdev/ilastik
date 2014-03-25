import os 
from functools import partial

from PyQt4 import uic
from PyQt4.QtCore import Qt, QEvent
from PyQt4.QtGui import QColor

from ilastik.applets.layerViewer.layerViewerGui import LayerViewerGui
from ilastik.utility.gui import threadRouted
from ilastik.utility import bind
from volumina.api import LazyflowSource, AlphaModulatedLayer
from lazyflow.operators.generic import OpSingleChannelSelector


class MriVolPreprocGui( LayerViewerGui ):
    
    def stopAndCleanUp(self):
        # Unsubscribe to all signals
        #for fn in self.__cleanup_fns:
        #    fn()
        # import pdb; pdb.set_trace()
        super(MriVolPreprocGui, self).stopAndCleanUp()

    def __init__(self, *args, **kwargs):
        # self.__cleanup_fns = []
        super( MriVolPreprocGui, self ).__init__(*args, **kwargs)
        self._channelColors = self._createDefault16ColorColorTable()

    def initAppletDrawerUi(self):
        """
        Reimplemented from LayerViewerGui base class.
        """
        # Load the ui file (find it in our own directory)
        localDir = os.path.split(__file__)[0]
        
        self._drawer = uic.loadUi(localDir+"/drawer.ui")
        '''
        self._drawer.applyButton.clicked.connect( self._onApplyButtonClicked )
        self._allWatchedWidgets = [ self._drawer.sigmaSpinBox ]
        
        # If the user pressed enter inside a spinbox, auto-click "Apply"
        for widget in self._allWatchedWidgets:
            widget.installEventFilter( self )
        '''
        '''
        self._updateGuiFromOperator()
        self.topLevelOperatorView.InputImage.notifyReady( bind(self._updateGuiFromOperator) )
        self.__cleanup_fns.append( partial( self.topLevelOperatorView.InputImage.unregisterUnready, bind(self._updateGuiFromOperator) ) )

        self.topLevelOperatorView.InputImage.notifyMetaChanged( bind(self._updateGuiFromOperator) )
        self.__cleanup_fns.append( partial( self.topLevelOperatorView.InputImage.unregisterMetaChanged, bind(self._updateGuiFromOperator) ) )
        '''

    def _updateOperatorFromGui(self):
        op = self.topLevelOperatorView
        # Read Sigma
        sigma = self._drawer.sigmaSpinBox.value()
        op.Sigma.setValue(sigma)
    '''    
    @threadRouted
    def _updateGuiFromOperator(self):
        op = self.topLevelOperatorView
    '''
    def _onApplyButtonClicked(self):
        self._updateOperatorFromGui()
        print 'Sigma value: {}'.format(self.topLevelOperatorView.Sigma)

    def eventFilter(self, watched, event):
        """
        If the user pressed 'enter' within a spinbox, auto-click the "apply" button.
        """
        if watched in self._allWatchedWidgets:
            if  event.type() == QEvent.KeyPress and\
              ( event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return):
                self._drawer.applyButton.click()
                return True
        return False
        
    def setupLayers(self):
        layers = []
        op = self.topLevelOperatorView

        if op.PredImage.ready():
            numChannels = op.PredImage.meta.getTaggedShape()['c']
            print 'Number of channels: {}'.format(numChannels)
            for channel in range(numChannels):
                channelProvider = OpSingleChannelSelector(parent=op.PredImage.getRealOperator().parent)
                channelProvider.Input.connect(op.PredImage)
                channelProvider.Index.setValue( channel )
                channelSrc = LazyflowSource( channelProvider.Output )
                inputChannelLayer = AlphaModulatedLayer( channelSrc,
                                                    tintColor=QColor(self._channelColors[channel]),
                                                    range=(0.0, 1.0),
                                                    normalize=(0.0, 1.0) )
                inputChannelLayer.opacity = 0.5
                inputChannelLayer.visible = True
                inputChannelLayer.name = "Input Channel " + str(channel)
                inputChannelLayer.setToolTip("Select input channel " + str(channel) + \
                                             " if this prediction image contains the objects of interest.")                    
                layers.append(inputChannelLayer)
        '''
        rawSlot = self.topLevelOperatorView.RawInput
        if rawSlot.ready():
            rawLayer = self.createStandardLayerFromSlot( rawSlot )
            rawLayer.name = "Raw data"
            rawLayer.visible = True
            rawLayer.opacity = 1.0
            layers.append(rawLayer)
        '''
        return layers


    def _createDefault16ColorColorTable(self):
        colors = []

        # SKIP: Transparent for the zero label
        #colors.append(QColor(0,0,0,0))

        # ilastik v0.5 colors
        colors.append( QColor( Qt.red ) )
        colors.append( QColor( Qt.green ) )
        colors.append( QColor( Qt.yellow ) )
        colors.append( QColor( Qt.blue ) )
        colors.append( QColor( Qt.magenta ) )
        colors.append( QColor( Qt.darkYellow ) )
        colors.append( QColor( Qt.lightGray ) )

        # Additional colors
        colors.append( QColor(255, 105, 180) ) #hot pink
        colors.append( QColor(102, 205, 170) ) #dark aquamarine
        colors.append( QColor(165,  42,  42) ) #brown
        colors.append( QColor(0, 0, 128) )     #navy
        colors.append( QColor(255, 165, 0) )   #orange
        colors.append( QColor(173, 255,  47) ) #green-yellow
        colors.append( QColor(128,0, 128) )    #purple
        colors.append( QColor(240, 230, 140) ) #khaki

        colors.append( QColor(192, 192, 192) ) #silver

#        colors.append( QColor(69, 69, 69) )    # dark grey
#        colors.append( QColor( Qt.cyan ) )

        assert len(colors) == 16
        return [c.rgba() for c in colors]