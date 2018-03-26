# RenderDoc Python console, powered by python 3.6.4.
# The 'pyrenderdoc' object is the current CaptureContext instance.
# The 'renderdoc' and 'qrenderdoc' modules are available.
# Documentation is available: https://renderdoc.org/docs/python_api/index.html
import importlib

import sys
sys.path.append('C:\\Users\\aleksandrbakanov\\Desktop\\RenderDocScripts')

import struct
import bufferutils

bufferutils.pyrenderdoc = pyrenderdoc

dcs = pyrenderdoc.CurDrawcalls()

filterDCID = 13827
evtStart = 13827
evtEnd = 14062
maxCount = -1
frameId = pyrenderdoc.FrameInfo().frameNumber
NullRID = renderdoc.ResourceId.Null()
output_name = 'C:\\Users\\aleksandrbakanov\\Desktop\\RenderDocScripts\\model_transparent.obj'

class drawcall:
	def __init__(self, evt):
		self.event = evt
		self.renderTextures = list()
		self.indexBuffer = None
		self.dataBuffers = list()
		pass

class objmesh:
	def __init__(self, name: str, dc):
		self.indices = list()
		self.vertices = list()
		self.texcoords = list()
		self.normals = list()
		self.myDc = dc
		self.name = name
	
	def _create_indices(self, indexStride):
		if indexStride != 2 and indexStride != 4:
			raise Exception('Only 2 or 4 indices stride are supported')
		
		fmt = 'H'
		if indexStride == 4:
			fmt = 'I'
		
		ibuflist = bufferutils.unpack_buffer(self.myDc.indexBuffer, self.myDc.indexBuffer.byteOffset, 0, indexStride, fmt)
		self.indices = ibuflist
	
	def _create_vertices(self, dataBufferId):
		buf = self.myDc.dataBuffers[dataBufferId]
		self.vertices = bufferutils.unpack_buffer(buf, buf.byteOffset, 0, buf.byteStride, 'fff')

	def _create_normals(self, dataBufferId):
		buf = self.myDc.dataBuffers[dataBufferId]
		self.normals = bufferutils.unpack_buffer(buf, buf.byteOffset, 0, buf.byteStride, 'fff')

	def _create_texuv(self, tcId, numFloats, dataBufferId):
		buf = self.myDc.dataBuffers[dataBufferId]
		self.texcoords = bufferutils.unpack_buffer(buf, buf.byteOffset, 0, buf.byteStride, 'f' * numFloats)

	def create(self, indexStride):
		self._create_indices(indexStride)

		db = self.myDc.dataBuffers;
		
		if len(db) >= 3:
			self._create_vertices(0)
			self._create_normals(1)
			self._create_texuv(0, 2, 2)
		elif len(db) == 2:
			# if second is TexCoords
			if len(db[1]) == 2:
				self._create_vertices(0)
				self._create_texuv(0, 2, 1)
			# if second is Normals
			else:
				self._create_vertices(0)
				self._create_normals(1)
		elif len(db) == 1:
			self._create_vertices(0)

	def show_info(self):
		print('Mesh stats:')
		print('Indices: %d' % len(self.indices))
		print('Vertices: %d' % len(self.vertices))
		print('Normals: %d' % len(self.normals))
		print('TexCoords: %d' % len(self.texcoords))
		
import objsaver
importlib.reload(objsaver)
obj_export = objsaver.ObjSaver()

def proceed_event(evt):
	pyrenderdoc.SetEventID([], evt.eventId, evt.eventId, True)
	
	psState = pyrenderdoc.CurD3D11PipelineState()
	iAss = psState.inputAssembly
	shader = psState.pixelShader
	
	#for l in iAss.layouts:
	#	format = l.format
	#
	#	print('Layout %d, %s: slot %d, offset %d' % (l.semanticIndex,l.semanticName, l.inputSlot, l.byteOffset))
	#	print('Format %s, width %d, count %d' % (format.compType, format.compByteWidth, format.compCount))

	myDc = drawcall(evt)

	#Print all textures
	for srv in shader.srvs:
		if srv.resourceResourceId == NullRID:
			continue
		
		texture = pyrenderdoc.GetTexture(srv.resourceResourceId)
		myDc.renderTextures.append(texture)

	#Print indices buffer
	#iBuf = 
	#print('Index buffer id: %d' % (iBuf.resourceId))
	myDc.indexBuffer = iAss.indexBuffer

	#Print All Mesh Buffers
	for buffer in iAss.vertexBuffers:
		rId = buffer.resourceId
		
		if rId == NullRID:
			continue
		
		myDc.dataBuffers.append(buffer)
		#print('Buffer for %d id %d' % (evt.eventId, rId))
	
	#print('-- -- DrawCall Data: %d buffers, %d textures' % (len(myDc.dataBuffers), len(myDc.renderTextures)))
	
	try:
		mesh = objmesh('Event%d' % evt.eventId, myDc)
		mesh.create(2)
		obj_export.add_mesh(mesh)
	except:
		print('Unable to create mesh on evt %d' % evt.eventId)
	#mesh.show_info()

for dc in dcs:
	if filterDCID >= 0 and dc.eventId != filterDCID:
		continue

	ndc = pyrenderdoc.GetDrawcall(pyrenderdoc.GetDrawcall(dc.eventId).previous)
	count = 0
	while True:
		ndc = ndc.next
		if ndc <= 0 or ndc > evtEnd:
			break
		
		count = count + 1
		if maxCount > 0 and count > maxCount:
			break

		ndc = pyrenderdoc.GetDrawcall(ndc)
		print('--Drawcall %s, %d' % (ndc.name, ndc.eventId))
		
		myEvt = ndc.events[-1]
		proceed_event(myEvt)
		
obj_export.save(output_name)

