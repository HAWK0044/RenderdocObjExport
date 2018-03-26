import struct
global pyrenderdoc

global bufData
def buffer_data_callback(ctrl, rId, offset, len):
	global bufData
	bufData = ctrl.GetBufferData(rId, offset, len)
	
def getbufferdata(rId, offset, len):
	global bufData
	rpm = pyrenderdoc.Replay()
	bufData = None

	rpm.BlockInvoke(lambda ctrl: buffer_data_callback(ctrl, rId, offset, len))
	return bufData

def unpack_buffer(buffer, offset, bufLen, stride, fmt):
	bufData = getbufferdata(buffer.resourceId, offset, bufLen)
	lenData = len(bufData)
	
	if lenData % stride != 0:
		raise Exception('Bad division %d on %d' % (lenData, stride))
	
	dataList = list()
	i = 0
	while i < lenData:
		dtUnit = struct.unpack_from(fmt, bufData, i)
		dataList.append(dtUnit)
		i = i + stride
	
	return dataList
