#!/usr/bin/python
"""
* Copyright (c) 2014, Franklin W. Olin College of Engineering

* All rights reserved.
*

* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*

* - Redistributions of source code must retain the above copyright notice,
* this list of conditions and the following disclaimer.
* - Redistributions in binary form must reproduce the above copyright notice,

* this list of conditions and the following disclaimer in the documentation
* and/or other materials provided with the distribution.
* - Neither the name of Franklin W. Olin College of Engineering nor the names

* of its contributors may be used to endorse or promote products derived
* from this software without specific prior written permission.
*

* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE

* ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
* LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
* CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF

* SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
* INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
* CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)

* ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
* POSSIBILITY OF SUCH DAMAGE.
*
*
"""

import os
import csv
import numpy as np

LEFT_HANDED = 0
RIGHT_HANDED = 1
RSL = 11            #RigidBody state vector length
MSL = 3 #Marker state vector length

bad = '#'

class Run():
    """Represents an experimental run as a collection of frames"""

    def __init__(self):
        self.rigidbodies = []
        self.frames = []
        self.rigidBody_frames = []
        self.coord_type = RIGHT_HANDED
        self.framecount = 0
        self.rigidbodycount = 0

        self.dir = None
        self.fi  = None

    def trk(self,id=None,name=None):
      """
      t,d = trk()

      Return marker data for rigidbody, specifying either id or name

      t - 1 x N - timestamp for N frames
      d - N x M x 3 - x,y,z data for M markers in N frames
      """
      ids = [t.id for t in self.rigidbodies]
      names = [t.name for t in self.rigidbodies]
      try:
        int(id)
      except:
        name = id
        id = None
      if name in names:
        id = ids[names.index(name)]
      #TODO ensure it only works with some set of markers. Re add functionality of `assert not(id is None)`
      if id == None:
        rigidbody= RigidBody(self.version)
        rigidbody.name = name
        rigidbody.id = len(self.rigidbodies)
        id = rigidbody.id
        ids.append (id)
        self.rigidbodies.append(rigidbody)

      tr = self.rigidbodies[ids.index(id)]
      N = self.framecount 
      M = tr.num_markers

      t = np.nan*np.zeros(N)
      d = np.nan*np.zeros((N,M,3))

      for f in self.rigidBody_frames:
        if f.id == id:
          j = f.index
          if j >= N: #ignore weird data
            continue
          t[j] = f.timestamp

          data = np.asarray([m.pos.toArray() for m in f.ptcld_markers]);
          #for now ignore all non perfect data
          if data.shape[0] == M:
            d[j,:,:] = np.asarray([m.pos.toArray() for m in f.ptcld_markers])

      return t,d

    def data(self):
      """
      t,d,D,S = data()

      Return data

      t - 1 x N - timestamp for N frames
      d - N x M x 3 - x,y,z data for M markers in N frames
      D - N x M_l x 3 - x,y,z data for M_l markers in N frames from rigidbody l
      S - N x L x 6 - yaw,pitch,roll,x,y,z data for L rigidbodies in N frames
      """
      if not self.frames:
        return None,None,None,None
      #t,d = zip(*[(f.timestamp,[m.pos.toArray() for m in f.markers]) 
      #                                         for f in self.frames])
      #t = [f.timestamp for f in self.frames]
      #d = [[m.pos.toArray() for m in f.markers] for f in self.frames]
      t = []; d = []; D = [];
      S = np.nan*np.zeros((len(self.frames),self.rigidbodycount,6))
      for j,f in enumerate(self.frames):
        t.append(f.timestamp)
        d.append([m.pos.toArray() for m in f.markers])
        for s in f.rigidBody_states:
          S[j,s.id-1,:] = np.hstack((s.erot.toArray(),s.pos.toArray()))


      m = [len(dd) for dd in d]
      M = max(m)
      p = [np.nan*np.ones(3) for m in range(M)]

      d = [dd + p[len(dd):] for dd in d]

      return np.array(t),np.array(d),D,np.array(S)

    def ReadFile(self, data_dir, filename, N=np.inf):
        """Create a Run from a data file

        Args:
            data_dir: string directory name
            filename: string name of the file to load
        """
        self.dir = data_dir
        self.fi  = filename
        filename = os.path.join(data_dir, filename)
        fp = csv.reader(open(filename, "rU"))
        self.version = 1.0 #set default version
        try:
          while ( 1 ):
              if len( self.frames ) > N:
                break
              fields = fp.next()
              if fields[0].lower() == "comment":
                  pass
              elif fields[0].lower() == "righthanded":
                  self.coord_type = RIGHT_HANDED
              else:
                  self.coord_type = LEFT_HANDED
                  if fields[0].lower() == "info":
                      if fields[1].lower() == "framecount":
                          self.framecount = int(fields[2])
                      elif fields[1].lower() in ["trackablecount", "rigidbodycount"]:
                          self.rigidbodycount = int(fields[2])
                          if self.rigidbodycount > 0:
                              for i in range(self.rigidbodycount):
                                  self.rigidbodies.append(RigidBody(self.version, fp.next()))
                      elif fields[1].lower() == "version":
                          self.version = float(fields[2])
                  elif fields[0].lower() == "frame":
                      self.frames.append(Frame(self.version, fields))
                  elif fields[0].lower() in ["trackable", "rigidbody"]:
                      self.rigidBody_frames.append(RigidBodyFrame(self.version, fields))
        except StopIteration:
            pass

    def __repr__( self ):
      return "run = {'dir':%s,'fi':%s}" % (self.dir,self.fi)

class Frame():
    """Represents one frame of motion capture data"""
    def __init__(self, version, fields):
        """Constructor for a frame object"""
        if fields[0].lower() != "frame":
            raise Exception("You attempted to make a frame from something " +\
                            "that is not frame data.")

        self.rigidBody_states = []
        self.markers = []

        self.index = int(fields[1])
        self.timestamp = float(fields[2])
        self.rigidbody_count = int(fields[3])
        idx = 4

        if self.rigidbody_count > 0:
            for i in range(self.rigidbody_count):
                if not( bad in ''.join(fields[idx:idx+RSL]) ):
                    self.rigidBody_states.append(RigidBodyState( fields[idx:idx+RSL]))
                idx += RSL
        self.marker_count = int(fields[idx])
        idx += 1
        stride = 4
        if version == 1.1:
          stride = 5
        for i in range(self.marker_count):
            if not( bad in ''.join(fields[idx:idx+MSL]) ):
                self.markers.append(Marker(fields[idx+MSL], fields[idx:idx+MSL]))
            idx += stride
    def __repr__( self ):
      return "frame = {'index':%s,'t':%f,'m':%d,'l':%d}" % (self.index,self.timestamp,len(self.markers),self.rigidbody_count)

class RigidBodyFrame():
    """Represents extended frame information for frames containing
    rigidBodies."""

    def __init__(self, version, fields):
        """Constructor for a frame of extended rigidBody information"""
        self.markers = []
        self.ptcld_markers = []
        self.index = int(fields[1])
        self.timestamp = float(fields[2])
        self.name = fields[3]
        self.id = int(fields[4])
        self.last_tracked = int(fields[5])
        self.marker_count = int(fields[6])
        idx = 7
        #Store the rigidBody markers
        for i in range(self.marker_count):
            tracked = fields[idx + (self.marker_count-i)*MSL + self.marker_count*MSL +
                             i]
            quality = fields[idx + (self.marker_count-i)*MSL +
                             self.marker_count*MSL + self.marker_count + i]
            if not( bad in ''.join(fields[idx:idx+MSL]) ):
              self.markers.append(RigidBodyMarker(None, fields[idx:idx+MSL], tracked, quality))
            idx += MSL
        #Store the point cloud markers
        for i in range(self.marker_count):
            if not( bad in ''.join(fields[idx:idx+MSL]) ):
                self.ptcld_markers.append(Marker(None, fields[idx:idx+MSL]))
            idx += MSL

        self.mean_error = np.nan
        if not( bad in ''.join(fields[idx + 2*self.marker_count]) ):
            float(fields[idx + 2*self.marker_count])

    def __repr__( self ):
      return "rigidBody_frame = {'index':%s,'id':%s,'t':%f,'name':%s,'m':%d}" % (self.index,self.id,self.timestamp,self.name,len(self.ptcld_markers))

class Marker():
    """Represents a marker"""

    def __init__(self, id, pos):
        """Constructor for a marker object"""
        self.id = id
        self.pos = Position(pos)

    def __repr__( self ):
      return "marker = {'id':%s,'pos':%s}" % (self.id,self.pos)

class RigidBodyMarker(Marker):
    """An extended marker with some data related to tracking"""

    def __init__(self, id, pos, tracked, quality):
        """Constructor for a rigidbody marker"""
        Marker.__init__(self, id, pos)
        self.tracked = tracked
        self.quality = quality

    def __repr__( self ):
      return "trk_" + Marker.__repr__(self)

class RigidBodyState():
    """Represents the dynamic state of a rigidBody"""

    def __init__(self, fields):
        """Constructor for a rigidbody state object"""
        self.id = int(fields[0])
        self.pos = Position(fields[1:4])
        self.qrot = QRot(fields[4:8])
        self.erot = ERot(fields[8:11])

    def __repr__( self ):
      return "trk_state = {'id':%d,'pos':%s,'erot':%d}" % (self.id,self.pos,self.erot)

class RigidBody():
    """Represents a rigidbody object"""

    def __init__(self, version, fields=None):
        """Constructor for a rigidbody object"""
        self.name = None
        self.id = None
        self.num_markers = 0
        self.markers = []
        
        if fields == None:
			return;
        if fields[0].lower() not in ["trackable", "rigidbody"]:
            raise Exception("You attempted to make a rigidbody object from " +\
                            "data that does not represent a rigidbody.")

        self.name = fields[1]
        self.id = int(fields[2])
        self.num_markers = int(fields[3])
        self.markers = []
        idx = 4
        for i in range(self.num_markers):
            self.markers.append(Position(fields[idx:idx+MSL]))
            idx += MSL

    def __repr__( self ):
      return "trk = {'id':%d,'name':%s,'m':%d}" % (self.id,self.name,self.num_markers)

class Position():
    """A class representing the x,y,z position of a point in space"""

    def __init__(self, fields):
        """Constructor of for a position object"""

        self.x = float(fields[0])
        self.y = float(fields[1])
        self.z = float(fields[2])

    def toArray(self):
        return np.array([self.x, self.y, self.z])

    def __repr__( self ):
      return "[%f,%f,%f]" % (self.x,self.y,self.z)

class QRot():
    """A class representing a rotation using Quaternions"""

    def __init__(self, fields):
        """Constructor for a quaternion-based rotation"""
        self.qx = float(fields[0])
        self.qy = float(fields[1])
        self.qz = float(fields[2])
        self.qw = float(fields[3])

    def toArray(self):
        return np.array([self.qx, self.qy, self.qz, self.qw])

class ERot():
    """A class representing a rotation using Euler angles"""

    def __init__(self, fields):
        """Constructor for an Euler angle-based rotation using the 3-2-1 or
        yaw, pitch, roll sequence"""
        self.yaw = float(fields[0])
        self.pitch = float(fields[1])
        self.roll = float(fields[2])

    def toArray(self):
        return np.array([self.yaw, self.pitch, self.roll])

    def __repr__( self ):
      return "[%f,%f,%f]" % (self.yaw,self.pitch,self.roll)
