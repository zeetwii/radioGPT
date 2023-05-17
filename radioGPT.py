#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Radio GPT
# Author: ZeeTwii
# Copyright: 2023
# Description: A GNURadio module meant to convert wav files into RF audio
# GNU Radio version: 3.10.5.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import soapy



from gnuradio import qtgui

class radioGPT(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Radio GPT", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Radio GPT")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "radioGPT")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.audioRate = audioRate = 768e3
        self.sampleRate = sampleRate = 1e6
        self.quadRate = quadRate = audioRate*1
        self.centerFreq = centerFreq = 88e6

        ##################################################
        # Blocks
        ##################################################

        self.soapy_hackrf_sink_0 = None
        dev = 'driver=hackrf'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_hackrf_sink_0 = soapy.sink(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)
        self.soapy_hackrf_sink_0.set_sample_rate(0, int(sampleRate))
        self.soapy_hackrf_sink_0.set_bandwidth(0, 0)
        self.soapy_hackrf_sink_0.set_frequency(0, int(centerFreq))
        self.soapy_hackrf_sink_0.set_gain(0, 'AMP', True)
        self.soapy_hackrf_sink_0.set_gain(0, 'VGA', min(max(47, 0.0), 47.0))
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            centerFreq, #fc
            sampleRate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(True)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.mmse_resampler_xx_0 = filter.mmse_resampler_ff(0, (sampleRate/quadRate))
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/media/sf_GitHub/radioGPT/people-talking-in-small-room-6064.wav', True)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(10)
        self.analog_wfm_tx_0 = analog.wfm_tx(
        	audio_rate=int(audioRate),
        	quad_rate=int(quadRate),
        	tau=(75e-6),
        	max_dev=75e3,
        	fh=(-1.0),
        )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_wfm_tx_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.analog_wfm_tx_0, 0), (self.soapy_hackrf_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.mmse_resampler_xx_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.mmse_resampler_xx_0, 0), (self.analog_wfm_tx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "radioGPT")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_audioRate(self):
        return self.audioRate

    def set_audioRate(self, audioRate):
        self.audioRate = audioRate
        self.set_quadRate(self.audioRate*1)

    def get_sampleRate(self):
        return self.sampleRate

    def set_sampleRate(self, sampleRate):
        self.sampleRate = sampleRate
        self.mmse_resampler_xx_0.set_resamp_ratio((self.sampleRate/self.quadRate))
        self.qtgui_sink_x_0.set_frequency_range(self.centerFreq, self.sampleRate)
        self.soapy_hackrf_sink_0.set_sample_rate(0, int(self.sampleRate))

    def get_quadRate(self):
        return self.quadRate

    def set_quadRate(self, quadRate):
        self.quadRate = quadRate
        self.mmse_resampler_xx_0.set_resamp_ratio((self.sampleRate/self.quadRate))

    def get_centerFreq(self):
        return self.centerFreq

    def set_centerFreq(self, centerFreq):
        self.centerFreq = centerFreq
        self.qtgui_sink_x_0.set_frequency_range(self.centerFreq, self.sampleRate)
        self.soapy_hackrf_sink_0.set_frequency(0, int(self.centerFreq))




def main(top_block_cls=radioGPT, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
