from os import path, mkdir, listdir, remove, walk, rename, rmdir
from sys import exit
import re
import xml.etree.ElementTree as ET
import zipfile
import numpy
import shutil
from pathlib import Path as plpath
from math import ceil

# User settings
driveLetter = "F"
romsetFolder = driveLetter+":\\Romsets"
systemDirs = [d for d in listdir(romsetFolder) if path.isdir(path.join(romsetFolder, d))]
systemChoice = ""
systemName = ""
systemFolder = ""
xmdbDir = driveLetter+":\\Rom Tools\\No-Intro Database"
xmdb = ""
usaOnly = False

mergedParentFolder = driveLetter+":\\Roms\\Merged"
sortedParentFolder = driveLetter+":\\Roms\\Merged and Sorted"
onePerGameParentFolder = driveLetter+":\\Roms\\1G1R\\"

biasPriority = ["World","USA","En","Europe","Australia","Canada","Japan","Ja","France","Fr","Germany","De","Spain","Es","Italy","It","Norway","Brazil","Sweden","China","Zh","Korea","Ko","Asia","Netherlands","Russia","Ru","Denmark","Nl","Pt","Sv","No","Da","Fi","Pl","Unknown"]
zoneBiasValues = {
	"World" : 0,
    "U" : 0,
    "USA" : 0,
    "En" : 1,
    "E" : 2,
    "Europe" : 2,
    "A" : 3,
    "Australia" : 3,
    "Ca" : 4,
    "Canada" : 4,
    "J" : 5,
    "Japan" : 5,
    "Ja" : 5,
    "F" : 6,
    "France" : 6,
    "Fr" : 6,
    "G" : 7,
	"Germany" : 7,
	"De" : 7,
    "S" : 8,
    "Spain" : 8,
    "Es" : 8,
    "I" : 9,
    "Italy" : 9,
    "It" : 9,
    "No" : 10,
    "Norway" : 10,
    "Br" : 11,
    "Brazil" : 11,
    "Sw" : 12,
    "Sweden" : 12,
    "Cn" : 13,
    "China" : 13,
    "Zh" : 13,
    "K" : 14,
    "Korea" : 14,
    "Ko" : 14,
    "As" : 15,
    "Asia" : 15,
    "Ne" : 16,
    "Netherlands" : 16,
    "Ru" : 17,
    "Russia" : 17,
    "Da" : 18,
    "Denmark" : 18,
    "Nl" : 19,
    "Pt" : 20,
    "Sv" : 21,
    "No" : 22,
    "Da" : 23,
    "Fi" : 24,
    "Pl" : 25
}

compilationArray = ["2 Games in 1 -", "2 Games in 1! -", "2 Disney Games -", "2 Great Games! -", "2 in 1 -", "2 in 1 Game Pack -", "2-in-1 Fun Pack -", "3 Games in 1 -", "4 Games on One Game Pak", "Double Game!", "Double Pack", "2 Jeux en 1", "Crash Superpack", "Spyro Superpack", "Crash & Spyro Superpack"]
classicNESArray = ["Classic NES Series", "Famicom Mini", "Hudson Best Collection"]

# -------------- #
# Main functions #
# -------------- #

def main():
	global systemChoice
	global systemName
	global systemFolder
	global xmdb
	global mergedFolder
	global sortedFolder
	global onePerGameFolder

	systemChoices = makeChoice("Choose romset(s):", systemDirs, True)
	choice = makeChoice("\nWhat do you want to do?", [
		"Merge matching ROMs into archives",
		"Sort merged archives (must merge first)",
		"Sort \"best\" version from each merged archive (1G1R) (must merge first)",
		"Merge and sort all",
		"Merge and sort best",
		"Merge, sort all, and sort best"])
	# print("\nForcing choice \"Merge and sort all\".")
	# choice = 4
	if choice > 1:
		delMergedChoice = makeChoice("Delete merge folder when finished?", ["Yes", "No"])
	for sc in systemChoices:
		systemChoice = systemDirs[sc-1]
		systemName = systemChoice.split("(")[0].strip()
		systemFolder = driveLetter+":\\Romsets\\"+systemChoice
		for f in listdir(xmdbDir):
			if f.split("(")[0].strip() == systemName:
				xmdb = path.join(xmdbDir, f)
				break
		if xmdb == "":
			print("XMDB for current system not found.")
			print("Skipping current system.")
			continue
		mergedFolder = path.join(mergedParentFolder, systemName)
		sortedFolder = path.join(sortedParentFolder, systemName)
		onePerGameFolder = path.join(onePerGameParentFolder, systemName)
		if choice in [1,4,5,6]:
			mergeRoms(False)
		if choice in [2,4]:
			sortMergedArchives()
			if delMergedChoice == 1:
				shutil.rmtree(mergedFolder)
				if len(listdir(mergedParentFolder)) == 0:
					rmdir(mergedParentFolder)
		if choice in [3,5]:
			sortBestVersions()
			if delMergedChoice == 1:
				shutil.rmtree(mergedFolder)
				if len(listdir(mergedParentFolder)) == 0:
					rmdir(mergedParentFolder)
		if choice == 6:
			sortMergedArchives()
			sortBestVersions()
			if delMergedChoice == 1:
				shutil.rmtree(mergedFolder)
				if len(listdir(mergedParentFolder)) == 0:
					rmdir(mergedParentFolder)

def mergeRoms(verbose = True):
	print("\nMerging ROMs for "+systemName+".\n")
	# if path.exists(mergedFolder) and len(listdir(mergedFolder)) > 0:
	# 	choice = makeChoice("\nThe merge directory for this system already exists. Merge anyway?", ["Yes", "No"])
	# 	if choice == 2:
	# 		print("Skipping this system.")
	# 		return

	createDir(mergedParentFolder)
	createDir(mergedFolder)
	mergedRoms = []
	mergedClones = []
	unmergedClones = []
	alreadyMergedClones = []
	alreadyUnmergedClones = []
	skipAll = False
	contentsFileExists = False
	contentsFileLocation = path.join(mergedFolder, "[Contents].txt")
	if path.isfile(contentsFileLocation):
		contentsFileExists = True
		with open(contentsFileLocation) as file:
			currLineFlag = 0
			for l in file.readlines():
				line = l.strip()
				if line != "":
					if line == "= CONTAINS =":
						currLineFlag = 1
					elif line == "= MISSING =":
						currLineFlag = 2
					elif currLineFlag == 1:
						alreadyMergedClones.append(line)
					elif currLineFlag == 2:
						alreadyUnmergedClones.append(line)
	allFiles = [f for f in listdir(systemFolder) if path.isfile(path.join(systemFolder, f))]
	tree = ET.parse(xmdb)
	root = tree.getroot()
	numZoneds = len(root[0][1])
	step = (numZoneds // 20) + 1
	numCurrZoned = 0
	for currZoned in root[0][1]:
		allBiases = [bias.get("name") for bias in currZoned.findall("bias")]
		allZones = [bias.get("zone") for bias in currZoned.findall("bias")]
		allClones = [clone.get("name")+".zip" for clone in currZoned.findall("clone")]
		allClonesLower = [clone.lower() for clone in allClones]
		for file in allFiles:
			# if the file exists, but the capitalization is wrong (example: "Sega" instead of "SEGA", fix it
			# fileName = path.splitext(file)[0]
			fixedCap = False
			for i in range(len(allClones)):
				if file.lower() == allClonesLower[i] and file != allClones[i]:
					currFilePath = path.join(systemFolder, file)
					newFilePath = path.join(systemFolder, allClones[i])
					print("Capitalization fix:")
					renameArchiveAndContent(currFilePath, newFilePath, path.splitext(allClones[i])[0])
					fixedCap = True
					break
			if fixedCap:
				break
		mergeName = getBestMergeName(allBiases, allZones)[1]
		currMerge = path.join(mergedFolder, mergeName)
		# if conflict exists (which is very rare; example: Pokemon Stadium (Japan)), rename according to region
		if path.exists(currMerge):
			if not contentsFileExists:
				print("Attempting to resolve naming conflict for "+mergeName+"\n")
				mergeName = handleDuplicateName(mergeName, [path.splitext(clone)[0] for clone in allClones])
				currMerge = path.join(mergedFolder, mergeName)
			elif mergeName in alreadyUnmergedClones:
				if len(listdir(currMerge)) != len(allClones):
					print("Attempting to resolve naming conflict for "+mergeName+"\n")
					mergeName = handleDuplicateName(mergeName, [path.splitext(clone)[0] for clone in allClones])
					currMerge = path.join(mergedFolder, mergeName)
		allClonesList = list(dict.fromkeys(allClones))
		for clone in allClonesList:
			currCloneName = path.splitext(clone)[0]
			if (not contentsFileExists) or currCloneName in alreadyUnmergedClones:
				currClone = path.join(systemFolder, clone)
				cloneExists = False
				if path.isfile(currClone):
					cloneExists = True
				else:
					# if the current clone does not exist in the romset...
					if usaOnly and not "USA" in clone:
						currWrongName = "SKIP"
					else:
						print("\nThe following ROM was not found:")
						print(clone)
						if not contentsFileExists:
							currWrongName = "SKIP"
						else:
							print("\nAll clones for this game:")
							for c in allClonesList:
								print(path.splitext(c)[0])
							recommendations = [f for f in allFiles if f.startswith(clone.split("(")[0]+"(") and not path.splitext(f)[0] in alreadyMergedClones+mergedClones]
							if currCloneName+" [b].zip" in recommendations:
								print("Romset contains bad dump of this rom. Skipping.")
								currWrongName = "SKIP"
							else:
								cwn = guessOldName(recommendations, currCloneName)
								if cwn == 0:
									if skipAll:
										currWrongName = "SKIP"
									else:
										cwn = makeChoice("Which ROM in your romset matches the missing ROM? It will be renamed.", recommendations+["OTHER", "SKIP", "SKIP ALL"])
								if (not skipAll) or cwn > 0:
									if cwn == len(recommendations) + 1:
										print("Enter the exact name of this ROM file in your romset (with extension if the extension isn\'t ZIP), or type \"SKIP\" (no quotes) to skip this ROM.")
										currWrongName = input()
									elif cwn == len(recommendations) + 2:
										currWrongName = "SKIP"
									elif cwn == len(recommendations) + 3:
										currWrongName = "SKIP"
										skipAll = True
									else:
										currWrongName = recommendations[cwn-1]
									if (len(currWrongName) <= 4 or not "." in currWrongName[-4:]) and currWrongName != "SKIP":
										currWrongName = currWrongName + ".zip"
									currWrongClone = path.join(systemFolder, currWrongName)
					if currWrongName == "SKIP":
						print()
					elif path.isfile(currWrongClone):
						if zipfile.is_zipfile(currWrongClone):
							renameArchiveAndContent(currWrongClone, currClone, currCloneName)
						else:
							# fileExt = path.splitext(currWrongClone)[1]
							rename(currWrongClone, path.splitext(currClone)[0]+path.splitext(currWrongClone)[1]) # this is probably right?
						cloneExists = True
					else:
						print("\nInvalid name. Skipping.")
				if cloneExists:
					createDir(currMerge)
					shutil.copy(currClone, path.join(currMerge, clone))
					mergedRoms.append(clone)
					mergedClones.append(currCloneName)
				else:
					unmergedClones.append(currCloneName)
		if path.isdir(currMerge) and len(listdir(currMerge)) == 0:
			if path.isdir(currMerge):
				shutil.rmtree(currMerge)
		else:
			if verbose:
				print("Merged all versions of "+mergeName)
		numCurrZoned += 1
		if numCurrZoned % step == 0:
			print(str(round(numCurrZoned*100/numZoneds, 1))+"% - Merged "+str(numCurrZoned)+" of "+str(numZoneds)+".")

	contentsFile = open(contentsFileLocation,"w",encoding='utf-8',errors="replace")
	contentsFile.writelines("=== "+systemName+" ===\n")
	contentsFile.writelines("=== DO NOT MANUALLY EDIT THIS FILE ===\n")
	numMergedClones = len(mergedClones) + len(alreadyMergedClones)
	numUnmergedClones = len(unmergedClones)
	contentsFile.writelines("=== This romset contains "+str(numMergedClones)+" of "+str(numMergedClones+numUnmergedClones)+" known ROMs ===\n")
	print("\n=== This romset contains "+str(numMergedClones)+" of "+str(numMergedClones+numUnmergedClones)+" known ROMs ===")
	contentsFile.writelines("\n")
	contentsFile.writelines("= CONTAINS =\n")
	for clone in alreadyMergedClones:
		contentsFile.writelines(clone+"\n")
	for clone in mergedClones:
		contentsFile.writelines(clone+"\n")
	contentsFile.writelines("\n")
	contentsFile.writelines("= MISSING =\n")
	for clone in unmergedClones:
		contentsFile.writelines(clone+"\n")
	contentsFile.close()
	print("Saved output to "+contentsFileLocation)

	numGames = len([game for game in listdir(mergedFolder) if path.isdir(path.join(mergedFolder, game))])
	print("\nFinished merging "+str(len(mergedRoms))+" roms into "+str(numGames)+" archives.")
	unmergedRoms = []
	allFiles = [f for f in listdir(systemFolder) if path.isfile(path.join(systemFolder, f))] # updated for renamed files
	for file in allFiles:
		if not (file in mergedRoms or path.splitext(file)[0] in alreadyMergedClones):
			unmergedRoms.append(file)
	if len(unmergedRoms) > 0:
		print("\nDid not merge the following "+str(len(unmergedRoms))+" ROMs:\n")
		for rom in unmergedRoms:
			print(rom)

def sortMergedArchives(verbose=False):
	print("\nSorting merged ROMs.\n")
	if path.exists(sortedFolder) and len(listdir(sortedFolder)) > 0:
		print("\nThe sorted merge directory for this system already exists. Have you already created a merged set?")
		print("Skipping this system.")
		return
	allGames, zoneds, numGames, step, numCurrGame = sortGameStart(sortedParentFolder, sortedFolder)
	for game in allGames:
		_, region, isUnl, isUnrel, isComp, isCNES, isGBAV = sortGame(game, zoneds)
		copyToMergedFolder(sortedFolder, game, region, isUnl, isUnrel, isComp, isCNES, isGBAV)
		if verbose:
			print("Copied "+game+" to "+region)
		numCurrGame += 1
		if numCurrGame % step == 0:
			print(str(round(numCurrGame*100/numGames, 1))+"% - Sorted "+str(numCurrGame)+" of "+str(numGames)+".")
	print("\nFinished sorting ROMs.")

def sortBestVersions(verbose=False):
	print("\nGetting best version from each archive and sorting.")
	if path.exists(onePerGameFolder) and len(listdir(onePerGameFolder)) > 0:
		print("\nThe 1G1R directory for this system already exists. Have you already created a merged set?")
		print("Skipping this system.")
		return
	# a lot of this code is copied from sortMergedArchives; it's less efficient, but less work (and it doesn't really matter here anyway)
	allGames, zoneds, numGames, step, numCurrGame = sortGameStart(onePerGameParentFolder, onePerGameFolder)
	for game in allGames:
		allClones, region, isUnl, isUnrel, isComp, isCNES, isGBAV = sortGame(game, zoneds)
		bestRom = getBestGame([c for c in allClones if path.isfile(path.join(systemFolder, c+".zip"))])
		finalGame = copyToMergedFolder(onePerGameFolder, bestRom+".zip", region, isUnl, isUnrel, isComp, isCNES, isGBAV, True)
		rename(finalGame, path.join(plpath(finalGame).parent, game+".zip"))
		if verbose:
			print("Copied "+bestRom+" to "+region)
		numCurrGame += 1
		if numCurrGame % step == 0:
			print(str(round(numCurrGame*100/numGames, 1))+"% - Sorted "+str(numCurrGame)+" of "+str(numGames)+".")
	print("\nFinished sorting ROMs.")

# -------------- #
# Helper methods #
# -------------- #

def copyToMergedFolder(sortedMergedFolder, game, region, isUnlicensed, isUnreleased, isCompilation, isClassicNESSeries, isGBAVideo, is1G1R=False):
	regionDir = path.join(sortedMergedFolder, "["+region+"]")
	createDir(regionDir)
	if isUnlicensed or isUnreleased or isCompilation or isClassicNESSeries or isGBAVideo:
		if isUnlicensed:
			specialDir = path.join(regionDir, "[Unlicensed]")
		elif isUnreleased:
			specialDir = path.join(regionDir, "[Unreleased]")
		elif isCompilation:
			specialDir = path.join(regionDir, "[Compilation]")
		elif isClassicNESSeries:
			specialDir = path.join(regionDir, "[NES & Famicom]")
		else:
			specialDir = path.join(regionDir, "[GBA Video]")
		createDir(specialDir)
		newDir = path.join(specialDir, game)
		parentDir = specialDir
	else:
		newDir = path.join(regionDir, game)
		parentDir = regionDir
	if is1G1R:
		shutil.copy(path.join(systemFolder, game), newDir)
	else:
		shutil.copytree(path.join(mergedFolder, game), newDir)
	return path.join(parentDir, game)

def createDir(p):
	if not path.exists(p):
		mkdir(p)

def getAttributeSplit(name):
	mna = [s.strip() for s in re.split('\(|\)', name) if s.strip() != ""]
	mergeNameArray = []
	mergeNameArray.append(mna[0])
	if len(mna) > 1:
		for i in range(1, len(mna)):
			if not ("," in mna[i] or "+" in mna[i]):
				mergeNameArray.append(mna[i])
			else:
				arrayWithComma = [s.strip() for s in re.split('\,|\+', mna[i]) if s.strip() != ""]
				for att2 in arrayWithComma:
					mergeNameArray.append(att2)
	return mergeNameArray

def getBestGame(clones):
	zoneValues = []
	cloneScores = []
	sortedClones = sorted(clones)
	for clone in sortedClones:
		attributes = getAttributeSplit(clone)[1:]
		revCheck = [a for a in attributes if len(a) >= 3]
		versionCheck = [a[0] for a in attributes]
		betaCheck = [a for a in attributes if len(a) >= 4]
		protoCheck = [a for a in attributes if len(a) >= 5]
		currZoneVal = 99
		for i in range(len(biasPriority)):
			if biasPriority[i] in attributes:
				currZoneVal = i
				break
		zoneValues.append(currZoneVal)
		currScore = 100
		if "Rev" in revCheck:
			currScore += 30
		if "v" in versionCheck:
			currScore += 30
		if "Beta" in betaCheck or "Proto" in protoCheck:
			currScore -= 50
		if "Virtual Console" in attributes or "GameCube" in attributes or "Collection" in attributes:
			currScore -= 10
		if "Sample" in attributes or "Demo" in attributes:
			currScore -= 90
		cloneScores.append(currScore)
	bestZones = numpy.where(zoneValues == numpy.min(zoneValues))[0].tolist()
	finalZone = 99
	bestScore = -500
	for zone in bestZones:
		currScore = cloneScores[zone]
		if currScore >= bestScore:
			bestScore = currScore
			finalZone = zone
	return sortedClones[finalZone]

def getBestMergeName(biases, zones, indexOnly=False):
	zoneValues = []
	for zone in zones:
		currVal = zoneBiasValues.get(zone)
		if currVal is None:
			currVal = 99
		zoneValues.append(currVal)
	mergeIndex = numpy.min(zoneValues)
	if indexOnly:
		return mergeIndex, ""
	mergeName = biases[numpy.argmin(zoneValues)]
	mergeNameArray = getAttributeSplit(mergeName)
	regionIndex = 1
	for i in range(1, len(mergeNameArray)):
		if mergeNameArray[i] in biasPriority:
			# mergeName = "(".join(mergeNameArray[0:i]).strip()
			mergeName = mergeNameArray[0]
			for j in range(1,i):
				mergeName = mergeName + " (" + mergeNameArray[j] + ")"
			regionIndex = i+1
			break
	suffix = ""
	if len(mergeNameArray) > regionIndex:
		suffix = getSuffix(mergeNameArray[regionIndex:])
	mergeName = mergeName + suffix
	mergeName = mergeName.rstrip(".")
	return mergeIndex, mergeName

def getMatchingRegion(clones):
	try:
		matchingRegion = getAttributeSplit(clones[0])[1]
		for i in range(1, len(clones)):
			if matchingRegion != getAttributeSplit(clones[i])[1]:
				return ""
		return matchingRegion
	except:
		return ""

def getNewName(mergeNameOnly, firstFileName, numStr="first"):
	print("\nWhat do you want to add to the name of the "+numStr+" archive? Example: Tetris (YOUR INPUT)")
	try:
		defaultGuess = getAttributeSplit(firstFileName)[2]
		print("Press Enter without inputting anything for the default guess:")
		print(defaultGuess)
	except:
		defaultGuess = None
	nn = input()
	if nn == "":
		nn = defaultGuess
	if nn != "":
		return mergeNameOnly+" ("+nn+").zip"
	else:
		return mergeNameOnly+".zip"

def getSuffix(attributes):
	skippedAttributes = ["Rev", "Beta", "Virtual Console", "Proto", "Unl", "v", "SGB Enhanced", "GB Compatible", "Demo", "Promo", "Sample", "GameCube", "Promotion Card"]
	for att in attributes:
		if att in biasPriority:
			continue
		skip = False
		for skippedAtt in skippedAttributes:
			if att.startswith(skippedAtt):
				skip = True
				break
		if skip:
			continue
		if "Collection" in att:
			continue
		if att.count("-") >= 2:
			continue
		return " ("+att+")"
	return ""

def guessOldName(recommendations, ccn):
	currCloneName = ccn.replace("&amp;", "&")
	array1 = ["(Rev A)", "(Rev B)", "(Rev C)", "(Rev D)", "(Rev E)", "(Beta A)", "(Beta B)", "(Beta C)", "(Beta D)", "(Beta E)", "(Proto A)", "(Proto B)", "(Proto C)", "(Proto D)", "(Proto E)", "(USA, Australia)", "(USA, Europe)"]
	array2 = ["(Rev 1)", "(Rev 2)", "(Rev 3)", "(Rev 4)", "(Rev 5)", "(Beta 1)", "(Beta 2)", "(Beta 3)", "(Beta 4)", "(Beta 5)", "(Proto 1)", "(Proto 2)", "(Proto 3)", "(Proto 4)", "(Proto 5)", "(USA)", "(USA)"]
	for i in range(len(recommendations)):
		currRec = path.splitext(recommendations[i])[0].replace("&amp;", "&")
		# quick lazy fix; used only for my DS set
		if systemName == "Nintendo - Nintendo DS":
			print("===================================================================================")
			print(currCloneName)
			print(currRec)
			if currCloneName.startswith(currRec+" (En") or currCloneName.startswith(currRec.replace("(USA)", "(USA, Europe)"+" (En")) or currCloneName.startswith(currRec.replace("(USA)", "(USA, Australia)"+" (En")):
				return i+1
		for j in range(len(array1)):
			elem1 = array1[j]
			elem2 = array2[j]
			if currRec.replace(elem1, elem2) == currCloneName or currRec.replace(elem2, elem1) == currCloneName:
				return i+1
	return 0

def handleDuplicateName(mergeName, secondArchiveClones):
	mergeNameOnly = path.splitext(mergeName)[0]
	if "[BIOS]" in mergeName: # auto-merge BIOS files
		return mergeName
	firstFolder = path.join(mergedFolder, mergeName)
	firstArchiveClones = listdir(firstFolder)
	firstMatchingRegion = getMatchingRegion(firstArchiveClones)
	secondMatchingRegion = getMatchingRegion(secondArchiveClones)
	# rename first archive to region
	if firstMatchingRegion != "" and secondMatchingRegion == "":
		newName = mergeNameOnly+" ("+firstMatchingRegion+")"
		try:
			rename(firstFolder, path.join(mergedFolder, newName))
		except:
			pass
		return mergeName
	# rename second archive to region
	if firstMatchingRegion == "" and secondMatchingRegion != "":
		newName = mergeNameOnly+" ("+secondMatchingRegion+")"
		return newName
	# rename both archives to region
	if firstMatchingRegion != "" and secondMatchingRegion != "":
		newName1 = mergeNameOnly+" ("+firstMatchingRegion+")"
		try:
			rename(firstFolder, path.join(mergedFolder, newName1))
		except:
			pass
		newName2 = mergeNameOnly+" ("+secondMatchingRegion+")"
		return newName2
	# rename neither (merge)
	return mergeName

def makeChoice(question, choices, allowMultiple=False): # the placement of this function is unorganized, but it works fine; might change this later
	numChoices = len(choices)
	if numChoices == 0:
		print("Warning: A question was asked with no valid answers. Returning None.")
		return None
	if numChoices == 1:
		print("A question was asked with only one valid answer. Returning this answer.")
		return choices[0]
	print("\n"+question)
	for i in range(numChoices):
		print(str(i+1)+": "+choices[i])
	cInput = input().split(" ")
	if not allowMultiple:
		try:
			assert len(cInput) == 1
			choice = int(cInput[0])
			assert choice > 0 and choice <= numChoices
			return choice
		except:
			print("Invalid input.")
			return makeChoice(question, choices, allowMultiple)
	else:
		try:
			choices = [int(c) for c in cInput]
			for choice in choices:
				assert choice > 0 and choice <= numChoices
			return choices
		except:
			print("Invalid input.")
			return makeChoice(question, choices, allowMultiple)

def renameArchiveAndContent(currPath, newPath, newName):
	replaceArchive = False
	newFullFileName = ""
	fileExt = ""
	extractedFile = ""
	with zipfile.ZipFile(currPath, 'r', zipfile.ZIP_DEFLATED) as zippedClone:
		zippedFiles = zippedClone.namelist()
		if len(zippedFiles) > 1:
			print("\nThis archive contains more than one file. Skipping.")
		else:
			zippedClone.extract(zippedFiles[0], systemFolder)
			fileExt = path.splitext(zippedFiles[0])[1]
			extractedFile = path.join(systemFolder, zippedFiles[0])
			newFullFileName = path.splitext(newPath)[0]+fileExt
			rename(extractedFile, newFullFileName)
			replaceArchive = True
	if replaceArchive:
		remove(currPath)
		with zipfile.ZipFile(newPath, 'w', zipfile.ZIP_DEFLATED) as newZip:
			newZip.write(newFullFileName, arcname='\\'+newName+fileExt)
		remove(newFullFileName)
	print("Renamed "+path.splitext(path.basename(currPath))[0]+" to "+newName+"\n")

def sortGameStart(parentFolder, childFolder):
	createDir(parentFolder)
	createDir(childFolder)
	allGames = [game for game in listdir(mergedFolder) if path.isdir(path.join(mergedFolder, game))]
	tree = ET.parse(xmdb)
	root = tree.getroot()
	zoneds = [zoned for zoned in root[0][1]]
	numGames = len(allGames)
	step = (numGames // 20) + 1
	numCurrGame = 0
	return allGames, zoneds, numGames, step, numCurrGame

def sortGame(game, zoneds):
	roms = listdir(path.join(mergedFolder, game))
	region = "Error"
	isUnlicensed = False
	isUnreleased = False
	isCompilation = False
	isClassicNESSeries = False
	isGBAVideo = False
	for zoned in zoneds:
		allClones = [clone.get("name").replace("&amp;", "&") for clone in zoned.findall("clone")]
		if path.splitext(roms[0])[0] in allClones:
			if "Test Program" in allClones[0]:
				region = "Test Programs"
			elif "[BIOS]" in allClones[0]:
				region = "BIOS"
			else:
				allZones = [bias.get("zone") for bias in zoned.findall("bias")]
				regionIndex = getBestMergeName([], allZones, True)[0]
				isUnlicensed = "(Unl)" in allClones[0]
				isUnreleased = True
				for clone in allClones:
					if not "(Proto" in clone:
						isUnreleased = False
						break
				if systemName == "Nintendo - Game Boy Advance":
					isCompilation = False
					for comp in compilationArray:
						if game.startswith(comp):
							isCompilation = True
							break
					isClassicNESSeries = False
					for nes in classicNESArray:
						if game.startswith(nes):
							isClassicNESSeries = True
							break
					isGBAVideo = game.startswith("Game Boy Advance Video")
				if regionIndex == 0:
					region = "USA"
				elif regionIndex == 2:
					region = "Europe"
				elif regionIndex in [1,3,4]:
					region = "Other (English)"
				elif regionIndex == 5:
					region = "Japan"
				else:
					region = "Other (non-English)"
			break
	return allClones, region, isUnlicensed, isUnreleased, isCompilation, isClassicNESSeries, isGBAVideo

if __name__ == '__main__':
	main()