.. _installing:

Installing Python, ChipWhisperer, Drivers & Building Target Firmware
====================================================================

Windows XP/7
------------

Installing on Windows requires a few extra steps compared to Linux, as Linux normally comes with most of the required tools.

Python Setup
^^^^^^^^^^^^^

You may already have Python installed, in which case you can skip some of these steps. If you already have Python installed make sure it is
the correct version (2.7.x). Python 3.x will not work with this codebase.


Python & Required Packages
""""""""""""""""""""""""""

Windows does not (normally) come with Python installed. Download the latest release of Python 2.7 (NOT Python 3.x). It
is highly recommended to use 32-bit Python, as several of the dependant libraries only have 32-bit versions. First, install
Python:

1. `Python 2.7.6 <http://www.python.org/download/releases/2.7.6/>`_

Next, you need to install ``setuptools``, the best way of doing this is to use a special script called ``ez_setup``. This
is described on the `setuptools documentation site <https://pypi.python.org/pypi/setuptools#windows?>`_. Alternatively, simply
click the following link (assuming you've already installed Python!) and let it run:

2. `Get ez_setup.py program <https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py>`_
   
3. Open a command prompt (on XP: run->cmd, on Windows 7: search 'cmd' from search bar) and type::  

    easy_install configobj
	
   The results should look something similar to this:

   .. image:: /images/easy_install-configobj.png
   
   If easy_install *is not* working, you need to modify your system path (see sidebar). Assuming it is, continue to install other required packages::

	easy_install pyside
	easy_install pyqtgraph
	easy_install configobj


.. sidebar:: Python Path Settings

	When you installed Python, it may not have modified your system path. Generally this will make your life easier, although it's not required.
	This guide assumes you can run python commands such as easy_install.exe direct from the command line. If you cannot seem to do so, it's easy to
	fix that.
	
	First, you need to open the environmental variables editing dialog. On Windows 7 / 8 simply search for **environment** from the start menu, and you'll
	get an option to **Edit System Environment Variables**. On Windows XP you'll have to find the **System Properties** option in the control panel, then
	go to the **Advanced** tab.
	
	Finally open the **Environment Variables** dialog, and edit the *PATH* system variable to include::
	
		;C:\Python27;C:\Python27\Scripts
		
	.. image:: /images/pathmodify.png


Next, you have to install NumPy & SciPy which don't work with easy_install. Run the following Windows binary installers - Be sure you are downloading the
*win32-py2.7.exe* version. The *Direct Link for Windows* should be the correct version, but they may get changed in the future to default to another Python
(e.g. 3.x which we don't use) version. The installer itself will validate you downloaded the correct version of NumPy/SciPy for your python installation, so
the installation will fail anyway if you accidently download the wrong version.

5. `NumPy <http://sourceforge.net/projects/numpy/files/NumPy/>`_ (Direct Link for `Windows <http://sourceforge.net/projects/numpy/files/latest/download?source=files>`__)
6. `SciPy <http://sourceforge.net/projects/scipy/files/scipy/>`_ (Direct Link for `Windows <http://sourceforge.net/projects/scipy/files/latest/download?source=files>`__)
   
Assuming you are planning on using the ChipWhisperer Capture Rev2 hardware, you also require `PyUSB <http://sourceforge.net/projects/pyusb/>`_.
The easiest method is to again use easy_install, by opening a terminal and running::

    easy_install pyusb


.. _optional-ftdi:

Optional Packages
"""""""""""""""""

Note there are some optional packages you may want. Generally you can avoid them unless you have specific need of
the features they enable:

**FTD2XX**: `ftd2xx <https://github.com/snmishra/ftd2xx>`_ is required for SASEBO-W, SAKURA-G, and SASEBO-GII Support. To install
this package, `download a copy of the ftd2xx repository <https://github.com/snmishra/ftd2xx/archive/master.zip>`_ and 
unzip it somewhere. Then run the following where you unzipped it::

    python setup.py install

This package will also require you to install the `FTDI D2XX Drivers <http://www.ftdichip.com/Drivers/D2XX.htm>`_. In the preceeding
link simply find the correct driver for your OS Version & install that.

**MYSQL**: If you want to use the MySQL trace format (not used by default), you'll need to install `umysql <https://pypi.python.org/pypi/umysql>`_::

	easy_install umysql


Getting & Installing ChipWhisperer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Assuming you've got a working Python installation, the next step is to install & run ChipWhisperer itself. This requires you to get a copy
of ChipWhisperer, which you have two choices:

1. Check the `Latest Software Release Page <https://www.assembla.com/wiki/show/chipwhisperer/ChipWhisperer_Software_Firmware_Releases>`_. Download & unzip the file somewhere.
2. Clone the GIT Repository ``git://git.assembla.com/chipwhisperer.git`` somewhere.

Generally 'somewhere' will become your ChipWhisperer working directory. These examples assume you've chosen ``C:\chipwhisperer`` as your
working directory.

Once you've got the file, we run the Python install procedure again (setup.py). We slightly modify it to use the *develop* command to reflect
that the files will probably be changing frequently. Again open a terminal and run the following, adjusting paths as needed::

    cd c:\chipwhisperer\openadc\controlsw\python
    python setup.py develop
    cd c:\chipwhisperer\software
    python setup.py develop

If you wish to confirm the installation worked, you can run ChipWhispererAnalyzer in the same terminal::

    cd c:\chipwhisperer\software\chipwhisperer\analyzer
    python ChipWhispererAnalyzer.py
    
Alternatively you can just double-click on ``ChipWhispererAnalyzer.py`` from Windows explorer, which should run the file using
Python.

You can see a `Video <http://www.youtube.com/watch?v=qd86cUD8iBs&hd=1>`__ of the Installation Procedure:

|YouTubeWin7Install|_

.. |YouTubeWin7Install| image:: /images/youtube-win7-install.png
.. _YouTubeWin7Install: http://www.youtube.com/watch?v=qd86cUD8iBs&hd=1

Installing Hardware Drivers for CaptureRev2
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following is specific to ChipWhisperer Capture Rev2 hardware. Using the mini-usb cable, plug in the ChipWhisperer Capture Rev2. Note
that only an internal LED will turn on when this happens - the LEDs on the front panel are controlled by the internal FPGA. They will not
be active until you actually communicate with the unit.

Windows should pop up a *New Hardware Found* dialog, but frequently may not. In which case force the driver to update using the following:

1. Open the *Device Manager*. On Windows 7 simply search *Device Manager* from start menu
2. Find the Cypress EZ-USB Item, which should have a yellow (!) mark
3. Click *Update Driver*

4. Once this happens, you'll be able to point Windows to the location of the drivers. Specify ``c:\chipwhisperer\hardware\capture\chipwhisperer-rev2`` as this location.

Once the drivers are found, you'll have to install Java to run the FPGA loader program.

5. Install Java Runtime Environment (if not already installed) from `Oracle <http://java.com/en/download/index.jsp>`_. **NB:** Be careful
   when installating Java that you are not tricked into installing anything additional.
   
Finally, we can configure the ChipWhisperer-Capture software to communicate with the hadware. To do so you need to configure the
FPGA loader program, microcontroller program, and FPGA bitstream.

6. Run ChipWhisperer-Capture by double-clicking ChipWhispererCapture.py in ``c:\chipwhisperer\software\chipwhisperer\capture\``
7. Under the *Tools* menu select *Config CW Firmware*
8. In the pop-up dialog, you may need to configure the location of several files. If they are blank set as follows:

   a. FWLoader Location: ``c:\chipwhisperer\hardware\capture\chipwhisperer-rev2\ezusb-firmware\ztex-sdk\fwloader\FWLoader.jar``
   b. FPGA Bitstream Location: ``c:\chipwhisperer\hardware\capture\chipwhisperer-rev2\hdl\ztex_rev2_1.11c_ise\interface.bit``
   c. Firmware Location: ``c:\chipwhisperer\hardware\capture\chipwhisperer-rev2\ezusb-firmware\ztex-sdk\examples\usb-fpga-1.11\1.11c\openadc\OpenADC.ihx``
   
9. Under the *Tools* menu selection *Download CW Firmware* with the ChipWhisperer device attached. If this works you will see a message in the *Debug Logging*
   window about firmware upload successful. If this fails check the output of the console to see what went wrong.

You can see a `Video <http://www.youtube.com/watch?v=bj_Ul02exi8&hd=1>`__ of the Installation Process:

|YouTubeWin7Driver|_

.. |YouTubeWin7Driver| image:: /images/youtube-win7-driver.png
.. _YouTubeWin7Driver: http://www.youtube.com/watch?v=bj_Ul02exi8&hd=1

    
Building & Programming Example Targets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following section is **NOT REQUIRED** for your first attack - you can jump right to the tutorial if you wish. However you'll ultimately wish to
modify the code of the device under test, and these instructions tell you how. You should first follow the tutorial to confirm your system is working
before modifying the code however!

To build the code, you'll need to install WinAVR. 

1. Download & Install `WinAVR 20100110 <http://sourceforge.net/projects/winavr/files/WinAVR/20100110/WinAVR-20100110-install.exe>`_


.. sidebar:: WinAVR Path Settings

    By default, WinAVR is added to your system path. This means you can run ``avr-gcc``, ``make`` and other programs from your normal Windows command line.
    You may **not** want this on certain systems where you already have similar tools installed. In which case either uncheck the *Add WinAVR to Path* option,
    or edit your system path to remove the WinAVR directories.
   
    If you do not add it to the system path, you'll need a method of readding the WinAVR directories when you want to use WinAVR. To do so create a file
    called ``winavr.bat`` in ``C:\WinAVR-20100110`` with the following contents::
   
        set PATH=%PATH%;C:\WinAVR-20100110\bin;C:\WinAVR-20100110\utils\bin
        cmd
    
    Now when you want to run WinAVR (e.g. to continue the examples here), you can simply double-click on the ``winavr.bat`` file. This will configure the path
    for *just that terminal*, rather than every terminal you open.
   

Note that the default codebase *does not* include the cryptographic code we attack. Instead you are required to add this code into the system -- if the
external code changes, this may eventually be instead rolled into the main codebase. To setup the code, follow the following steps:

2.  Run the script ``get_crypto.bat`` inside the ``chipwhisperer\hardware\victims\firmware`` directory.
3.  **Only** if this script fails, try the following manual version instead (but try the automated version first!):
    
    a.  From the `avr-crypto-lib project <http://avrcryptolib.das-labor.org/trac>`_ download the following: `Nightly Tar Ball <http://avrcryptolib.das-labor.org/avrcryptolib-current.tar.bz2>`_
    b.  You'll need to extract the downloaded file. You can do this with programs built into WinAVR, the following shows some example commands::
            
            cd C:\Users\colin\Downloads
            bunzip2 avrcryptolib-current.tar.bz2
            tar -xvf avrcryptolib-current.tar
            
    c.  Copy everything in ``avrcryptolib-nightly\avrcryptolib\aes`` to ``c:\avrchipwhisperer\hardware\victims\firmware\crypto\avr-crypto-lib\aes`` (may need to created directory)
    d.  Copy everything in ``avrcryptolib-nightly\avrcryptolib\gf256mul`` to ``c:\avrchipwhisperer\hardware\victims\firmware\crypto\avr-crypto-lib\aes`` (same directory as above)

4.  ``cd`` to the directory with the avr-serial example, and run ``make atmega328p``::
    
        cd c:\chipwhisperer\hardware\victims\firmware\avr-serial
        make MCU=atmega328p

    If this is successful, you'll see an output like the following:

    .. image:: /images/avr-build-ok.png
    
    If instead you get an error something like ``make: *** No rule to make target `simpleserial.elf', needed by `elf'.  Stop.``, this means a required file was missing. Check
    that you have copied all files to the ``avr-crypto-lib\aes directory``, in particular did you copy the two *gf256mul* files? 

5.  Next, you will need to program the AVR itself. On Windows we will make use of the free `Atmel Studio 4.19 <www.atmel.com/tools/STUDIOARCHIVE.aspx>`_. You can find a direct link here:
    `Direct Link to Atmel Studio 4.19 Binary <http://www.atmel.com/System/BaseForm.aspx?target=tcm:26-17924>`_ which will require you to enter an email address to receive the
    download link.  Note it is possible to use ``avrdude``, a command-line program which is part of WinAVR instead if you wish. However since many people find the graphical interface
    of AVRStudio easier, this guide will use AVRStudio. Be sure to install the USB drivers as part of the package.

6.  Plug in the USB-A Connector on the rear side of the ChipWhisperer Rev2. This should trigger the driver installation, which will detect the device as a *AVR-ISP MK2*.

7.  Once AVR Studio is installed, open the main window. From the toolbar select either the *Con* or *AVR* icon, and select the *AVR-ISP MK-II* Device:
    
    .. image:: /images/studio4-connect.png

8.  In the window that opens, select the *Main* tab. Select the device type as *AtMega328P*, and hit *Read Signature*. You should get an indication that the device signature was
    successfully read!

    .. image:: /images/studio4-read-signature.png
    
9.  Finally we can program the chip. To do so switch to the *Program* tab, select the ``simpleserial.hex`` file that was generated in Step 4, and hit *Program*. If it's successful
    you should see some output data saying so.
    
    .. image:: /images/studio4-program.png

You can see a `Video <http://www.youtube.com/watch?v=gy6-MBvVvy4&hd=1>`__ of the Target Build Procedure:

|YouTubeWin7Target|_

.. |YouTubeWin7Target| image:: /images/youtube-win7-target.png
.. _YouTubeWin7Target: http://www.youtube.com/watch?v=gy6-MBvVvy4&hd=1

Linux
-------

Python Setup
^^^^^^^^^^^^^^^

On Linux, installing Python & all the associated packages is much easier than on Windows. Typically you can install them from a package manager, if you are
using Fedora Core or similar, just type::

    $ sudo yum install python27 python27-devel python27-libs python-pyside numpy scipy python-configobj pyusb

On Ubuntu or similar:

    $ sudo apt-get install python2.7 python2.7-dev python2.7-libs python-numpy python-scipy python-pyside python-configobj python-usb python-setuptools

    
You also need to install `PyQtGraph <http://www.pyqtgraph.org/>`_ which is not normally in those repositories. See the PyQtGraph website
for either a Debian/Ubuntu package, or information about installing from source.

Getting ChipWhisperer
^^^^^^^^^^^^^^^^^^^^^^^

As in the Windows release, you can download a complete ChipWhisperer software release. Alternatively you can clone the
ChipWhisperer repository with git, which is very simple on Linux:

    $ git clone
    $ cd chipwhisperer
    $ git clone 
    
Be aware that the git code may be broken, although we try not to commit completely untested code to the master branch. Either way
once you have the `chipwhisperer` directory somewhere, do the following from within that directory:

    $ cd software
    $ sudo python setup.py develop
    $ cd ../openadc/controlsw/python
    $ sudo python setup.py develop

**NB:**This assumes the `python` command links to Python-2.7, and not Python-3.x. You may need to specify either `python2.7` or `python27`
as the command instead of python to force this.

ChipWhisperer Rev2 Capture Hardware Driver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The *driver* for Linux is built in, however you need to allow your user account to access the peripheral. To do so, 
you'll have to make a file called ``/etc/udev/rules.d/99-ztex.rules`` . The contents of this file should be::

    # allow users to claim the device
    SUBSYSTEM=="usb", ATTRS{idVendor}=="04b4", ATTRS{idProduct}=="8613", MODE="0664", GROUP="plugdev"
    SUBSYSTEM=="usb", ATTRS{idVendor}=="221a", ATTRS{idProduct}=="0100", MODE="0664", GROUP="plugdev"

Then add your username to the plugdev group::

    $ sudo usermod -a -G plugdev YOUR-USERNAME

And reset the udev system::

    $ sudo udevadm control --reload-rules

Finally log out & in again for the group change to take effect. 


FTDI Hardware Driver (SASEBO-W, SAKURA-G, SASEBO-GII)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**This is only required for supporting FTDI-connected hardware** such as the SASEBO-W, SAKURA-G, SASEBO-GII. This is NOT
required for the ChipWhisperer Capture Rev2.

First, you need to install the D2XX drivers & python module. See the section :ref:`optional-ftdi`.

Currently, there is a bit of a hack needed. You have to create (or modify if it exists) the file ``/etc/udev/rules.d/99-libftdi.rules`` .
The following modifications will cause **any FTDI-serial device to stop working**, so backup the existing file! The contents of this file should be::

    SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010", MODE="0664", GROUP="plugdev"
    ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010", RUN+="/bin/sh -c 'echo $kernel > /sys/bus/usb/drivers/ftdi_sio/unbind'"

Then add your username to the plugdev group::

    $ sudo usermod -a -G plugdev YOUR-USERNAME

And reset the udev system::

    $ sudo udevadm control --reload-rules

Finally log out & in again for the group change to take effect. 


