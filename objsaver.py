class ObjSaver:
	def __init__(self):
		self.meshes = list()
		pass
		
	def add_mesh(self, mesh):
		self.meshes.append(mesh)
	
	def save(self, name: str):
		file = open(name, 'w')
		
		verts_count = 1
		for mesh in self.meshes:
			numIndices = len(mesh.indices)
			#print('Saving mesh %s' % mesh.name)
			
			file.write('g %s\n' % mesh.name)
			for v in mesh.vertices:
				file.write('v %f %f %f\n' % (v[0], v[1], v[2]))
				
			for n in mesh.normals:
				file.write('vn %f %f %f\n' % (n[0], n[1], n[2]))
				
			for t in mesh.texcoords:
				file.write('vt %f %f\n' % (t[0], t[1]))
			
			id = 0
			for x in range(0, int(numIndices // 3)):
				i1 = mesh.indices[id+0][0] + verts_count
				i2 = mesh.indices[id+1][0] + verts_count
				i3 = mesh.indices[id+2][0] + verts_count
				
				#print('%d' % i1)
				file.write('f %d/%d/%d %d/%d/%d %d/%d/%d\n' % (i1,i1,i1,i2,i2,i2,i3,i3,i3))
					
				id = id + 3
			
			verts_count = verts_count + len(mesh.vertices)
			file.write('#Object %s\n' % mesh.name)
			
		file.close()
