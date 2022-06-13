# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

class CentroidTracker():
	def __init__(self, maxDisappeared=0): ## 1 was working but sometime creating issues
		# initialize the next unique object ID along with two ordered
		# dictionaries used to keep track of mapping a given object
		# ID to its centroid and number of consecutive frames it has
		# been marked as "disappeared", respectively
		self.nextObjectID = 1
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()
		self.oldCentroids = OrderedDict() ##### ---------------- Custom code for storing old centroids
		

		self.BBox = OrderedDict()
		# store the number of maximum consecutive frames a given
		# object is allowed to be marked as "disappeared" until we
		# need to deregister the object from tracking
		self.maxDisappeared = maxDisappeared

	def register(self, centroid,BBox,x_mid,movement_direction):
		# print(f"-!!!!!!!!!!!!!!! inside register function 1st line.")
		# when registering an object we use the next available object
		# ID to store the centroid

		# if self.nextObjectID >1:
		# 	if_existed = [ tuple(coc) for coc in list(self.objects[self.nextObjectID-1]) if tuple(coc) == tuple(centroid)]
			
		# else:
		# 	if_existed = []

		# if len(if_existed)>0:
		# 	print(f"This centroid:{centroid} already existed!!! skipping")

		# else:


		if movement_direction =='left2right':
			# print(f'XX movement is left2right XX')
			if centroid[0] < x_mid :
			# if centroid[0] > x_mid or centroid[0] < x_mid  :

				self.objects[self.nextObjectID] = centroid
				self.disappeared[self.nextObjectID] = 0 ### 0 - was giving good result in truck
				self.oldCentroids[self.nextObjectID] = [centroid] ##### ---------------- Custom code for storing old centroids
				

				self.BBox[self.nextObjectID] = BBox

				# print(f"\n------- new object Created as : {self.objects}")
				# print(f"------- new oldCentroid object Created as : {self.oldCentroids}")
				# print(f"------- new BBoxe  Created as : {self.BBox}")

				self.nextObjectID += 1 

		else: ### movement is right2left
			# print(f'XX movement is right2left XX')

			if centroid[0] > x_mid :
			# if centroid[0] > x_mid or centroid[0] < x_mid  :

				self.objects[self.nextObjectID] = centroid
				self.disappeared[self.nextObjectID] = 0 ### 0 - was giving good result in truck
				self.oldCentroids[self.nextObjectID] = [centroid] ##### ---------------- Custom code for storing old centroids
				

				self.BBox[self.nextObjectID] = BBox

				# print(f"\n------- new object Created as : {self.objects}")
				# print(f"------- new oldCentroid object Created as : {self.oldCentroids}")
				# print(f"------- new BBoxe  Created as : {self.BBox}")

				self.nextObjectID += 1


	def deregister(self, objectID):
		# to deregister an object ID we delete the object ID from
		# both of our respective dictionaries
		del self.objects[objectID]
		del self.disappeared[objectID]

		del self.oldCentroids[objectID]  ##### ---------------- Custom code for storing old centroids
		del self.BBox[objectID]

		# print(f"XXX -------------------- DE-REGISTERING the id : {objectID}----")

	def update(self, rects,x_mid,movement_direction):

		# print(f"********************************************************* rects 1st line update: {rects}")
		# check to see if the list of input bounding box rectangles
		# is empty
		if len(rects) == 0:
			# loop over any existing tracked objects and mark them
			# as disappeared
			for objectID in list(self.disappeared.keys()):
				self.disappeared[objectID] += 1

				# if we have reached a maximum number of consecutive
				# frames where a given object has been marked as
				# missing, deregister it
				if self.disappeared[objectID] > self.maxDisappeared:
					# print(f"------------- Deregistering as len(rects) ==0 and self.disappeared is : {self.disappeared[objectID]} --------DDDDDDDRRRRRRRxx")
					self.deregister(objectID)

			# return early as there are no centroids or tracking info
			# to update
			return self.objects

		# initialize an array of input centroids for the current frame
		inputCentroids = np.zeros((len(rects), 2), dtype="int")

		BBoxXes = np.zeros((len(rects), 4), dtype="int")

		# loop over the bounding box rectangles
		for (i, (startX, startY, endX, endY)) in enumerate(rects):
			# use the bounding box coordinates to derive the centroid
			cX = int((startX + endX) / 2.0)
			cY = int((startY + endY) / 2.0)
			inputCentroids[i] = (cX, cY)
			BBoxXes[i] = (startX, startY, endX, endY)

		# if we are currently not tracking any objects take the input
		# centroids and register each of them
		if len(self.objects) == 0:
			for i in range(0, len(inputCentroids)):
				# print(f"------------- Registering as starting NEW ----------------------------- NNNNNNNNNNNNNNNNNNNNNN")
				self.register(inputCentroids[i], BBoxXes[i],x_mid,movement_direction)

		# otherwise, are are currently tracking objects so we need to
		# try to match the input centroids to existing object
		# centroids
		else:
			# grab the set of object IDs and corresponding centroids
			objectIDs = list(self.objects.keys())
			objectCentroids = list(self.objects.values())

			# compute the distance between each pair of object
			# centroids and input centroids, respectively -- our
			# goal will be to match an input centroid to an existing
			# object centroid
			D = dist.cdist(np.array(objectCentroids), inputCentroids)

			# in order to perform this matching we must (1) find the
			# smallest value in each row and then (2) sort the row
			# indexes based on their minimum values so that the row
			# with the smallest value as at the *front* of the index
			# list
			rows = D.min(axis=1).argsort()

			# next, we perform a similar process on the columns by
			# finding the smallest value in each column and then
			# sorting using the previously computed row index list
			cols = D.argmin(axis=1)[rows]

			# print(f"--------------- rows {rows}")

			# print(f"--------------- cols: {cols}")

			# in order to determine if we need to update, register,
			# or deregister an object we need to keep track of which
			# of the rows and column indexes we have already examined
			usedRows = set()
			usedCols = set()

			# loop over the combination of the (row, column) index
			# tuples
			for (row, col) in zip(rows, cols):
				# if we have already examined either the row or
				# column value before, ignore it
				# val
				if row in usedRows or col in usedCols:
					continue

				# print(f"oldcentroid : {self.oldCentroids} ----------------- OOOOOOOOOOOOOOOOOOOOOOOOO CCCCCCCCCCCCCCCCCC")
				# print(f"BBoxes : {self.BBox} ----------------- BBBBBBBBBBBBBBBBBooooooooooooooXXXXXXXXXXXXXX\n\n")

				objectID = objectIDs[row]

				oldc = [c[0] for c in self.oldCentroids[objectID]]

				if len(oldc) > 30: #### this is if the belt stopped and bag is at a perticular location and bboxes flacuates 
					
					# self.oldCentroids[objectID] = [c for c in self.oldCentroids[objectID][1:11] ] ### test this theory 
					oldc = oldc[1:29] ### 1:11 --- giving good result
					# print(f"\n len of oldc > 30 hence keeping only last 10 data as : {oldc}")
				
				# oldc = [c[0] for c in [self.oldCentroids[k] for k in self.oldCentroids.keys()]]  ##### ---------------- Custom code for storing old centroids

				direction = inputCentroids[col][0] - np.mean(oldc) ##### ---------------- Custom code for storing old centroids

				# print(f"Old centroid X-coordinates list: {oldc}")
				# print(f"current centroid: {inputCentroids[col][0]} - old centroid mean : {np.mean(oldc)}")
				# print(f"current centroid for updating: {inputCentroids[col]} and direction is : {direction}")


				if movement_direction =='left2right':
					
				
					if direction >=0:    ##### ---------------- Custom code for storing old centroids


						# otherwise, grab the object ID for the current row,
						# set its new centroid, and reset the disappeared
						# counter
						# objectID = objectIDs[row]

						# print(f"---------------------------------- objects w.r.t to current ID\n{self.objects[objectID]}")
						self.objects[objectID] = inputCentroids[col]
						# print(f"---------------------------------- objects w.r.t to current ID after updation \n{self.objects[objectID]}")

						self.disappeared[objectID] = 0

						self.oldCentroids[objectID].append(inputCentroids[col])    ##### ---------------- Custom code for storing old centroids

						self.BBox[objectID] = BBoxXes[col] ### updating bboxes

					elif direction<0:
						# print(f"Deregistering as object is moving from left2right and direction: {direction} < 0")
						self.deregister(objectID)
					usedRows.add(row)
					usedCols.add(col)

				else:  ### movement is right2left
					if direction <=0:    ##### ---------------- Custom code for storing old centroids

						# otherwise, grab the object ID for the current row,
						# set its new centroid, and reset the disappeared
						# counter
						# objectID = objectIDs[row]

						# print(f"---------------------------------- objects w.r.t to current ID\n{self.objects[objectID]}")
						self.objects[objectID] = inputCentroids[col]
						# print(f"---------------------------------- objects w.r.t to current ID after updation \n{self.objects[objectID]}")

						self.disappeared[objectID] = 0

						self.oldCentroids[objectID].append(inputCentroids[col])    ##### ---------------- Custom code for storing old centroids

						self.BBox[objectID] = BBoxXes[col] ### updating bboxes

					elif direction>0:
						# print(f"Deregistering as object is moving from right2left and direction: {direction} > 0")

						self.deregister(objectID)
					usedRows.add(row)
					usedCols.add(col)

				# indicate that we have examined each of the row and
				# column indexes, respectively
				# usedRows.add(row)
				# usedCols.add(col)

			# compute both the row and column index we have NOT yet
			# examined
			unusedRows = set(range(0, D.shape[0])).difference(usedRows)
			unusedCols = set(range(0, D.shape[1])).difference(usedCols)

			# in the event that the number of object centroids is
			# equal or greater than the number of input centroids
			# we need to check and see if some of these objects have
			# potentially disappeared
			# print(f"------------------------------------------------------------- UnusedCols: {unusedCols}")

			if D.shape[0] >= D.shape[1]:
				# loop over the unused row indexes
				for row in unusedRows:
					# grab the object ID for the corresponding row
					# index and increment the disappeared counter
					objectID = objectIDs[row]
					self.disappeared[objectID] += 1

					# check to see if the number of consecutive
					# frames the object has been marked "disappeared"
					# for warrants deregistering the object
					if self.disappeared[objectID] > self.maxDisappeared:
						# print(f"------------- Deregistering as D.shape[0] >= D.shape[1] and self.disappeared is : {self.disappeared[objectID]}--------DDDDDDDDDDDDDDRRRRRRRRR")
						self.deregister(objectID)

			# otherwise, if the number of input centroids is greater
			# than the number of existing object centroids we need to
			# register each new input centroid as a trackable object
			else:
				for col in unusedCols:
					# print(f"------------- Registering as col in unusedCols. i.e. new objects found ----------------------------- NNNNNNNNNNNNNNNNNNNNNN")
					# print(inputCentroids[col], BBoxXes[col], x_mid)
					
					self.register(inputCentroids[col], BBoxXes[col], x_mid,movement_direction)

		# return the set of trackable objects
		return self.objects