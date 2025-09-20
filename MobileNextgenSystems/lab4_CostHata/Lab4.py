#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Vladimir Ponomarenko
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
import sip



class Lab4(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Vladimir Ponomarenko", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Vladimir Ponomarenko")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
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

        self.settings = Qt.QSettings("GNU Radio", "Lab4")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.zmq_timeout = zmq_timeout = 100
        self.zmq_hwm = zmq_hwm = -1
        self.samp_rate = samp_rate = 23.04e6
        self.path_loss_db = path_loss_db = 0
        self.noise = noise = 0.0005

        ##################################################
        # Blocks
        ##################################################

        self._path_loss_db_range = qtgui.Range(0, 300, 1, 0, 200)
        self._path_loss_db_win = qtgui.RangeWidget(self._path_loss_db_range, self.set_path_loss_db, "Pathloss [dB]", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._path_loss_db_win)
        self._noise_range = qtgui.Range(0, 0.1, 0.0001, 0.0005, 200)
        self._noise_win = qtgui.RangeWidget(self._noise_range, self.set_noise, "Noise Amplitude", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._noise_win)
        self.zeromq_req_source_1 = zeromq.req_source(gr.sizeof_gr_complex, 1, 'tcp://localhost:2002', zmq_timeout, False, zmq_hwm, False)
        self.zeromq_req_source_0 = zeromq.req_source(gr.sizeof_gr_complex, 1, 'tcp://localhost:2000', zmq_timeout, False, zmq_hwm, False)
        self.zeromq_rep_sink_0_1 = zeromq.rep_sink(gr.sizeof_gr_complex, 1, 'tcp://*:2101', zmq_timeout, False, zmq_hwm, True)
        self.zeromq_rep_sink_0 = zeromq.rep_sink(gr.sizeof_gr_complex, 1, 'tcp://*:2003', zmq_timeout, False, zmq_hwm, True)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.blocks_throttle2_0_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_cc(10**(-1.0*path_loss_db/20.0))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(10**(-1.0*path_loss_db/20.0))
        self.blocks_add_xx_0_0 = blocks.add_vcc(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_noise_source_x_0_0 = analog.noise_source_c(analog.GR_GAUSSIAN, noise, 0)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, noise, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_noise_source_x_0_0, 0), (self.blocks_add_xx_0_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.zeromq_rep_sink_0, 0))
        self.connect((self.blocks_add_xx_0_0, 0), (self.zeromq_rep_sink_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_throttle2_0_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.zeromq_req_source_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.zeromq_req_source_1, 0), (self.blocks_throttle2_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "Lab4")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_zmq_timeout(self):
        return self.zmq_timeout

    def set_zmq_timeout(self, zmq_timeout):
        self.zmq_timeout = zmq_timeout

    def get_zmq_hwm(self):
        return self.zmq_hwm

    def set_zmq_hwm(self, zmq_hwm):
        self.zmq_hwm = zmq_hwm

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle2_0_0.set_sample_rate(self.samp_rate)
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_path_loss_db(self):
        return self.path_loss_db

    def set_path_loss_db(self, path_loss_db):
        self.path_loss_db = path_loss_db
        self.blocks_multiply_const_vxx_0.set_k(10**(-1.0*self.path_loss_db/20.0))
        self.blocks_multiply_const_vxx_0_1.set_k(10**(-1.0*self.path_loss_db/20.0))

    def get_noise(self):
        return self.noise

    def set_noise(self, noise):
        self.noise = noise
        self.analog_noise_source_x_0.set_amplitude(self.noise)
        self.analog_noise_source_x_0_0.set_amplitude(self.noise)




def main(top_block_cls=Lab4, options=None):

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
