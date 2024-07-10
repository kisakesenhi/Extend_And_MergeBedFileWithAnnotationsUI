import os
import shutil
import os.path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

bedfile=None
ExtendValue=None

#UI GET FUNCTIONS

def get_bedfile():
    global bedfile
    bedfile_userprovided=tk.filedialog.askopenfilename(defaultextension=".bed",filetypes=[("Bed File",".bed"),("All Files", "*.*") ] )
    if os.path.isfile(bedfile_userprovided):
        bedfile=bedfile_userprovided
        #update text field
        bed_text.config(state='normal')
        bed_text.delete('1.0','end')
        bed_text.insert('end',bedfile)
        bed_text.config(state='disabled')

def set_ExtendEntry():
    #set the glbal ExtendValue and returns True or False
    global ExtendValue
    Extend_String=extendEntry.get()
    try:
        value=int(Extend_String.strip())
        ExtendValue=value
        return True
    except:
        tk.messagebox.showinfo("Error",f"The Value on Extend file '{Extend_String}' is not a numberic value\nPlease enter a numeric value")
        return False

def apply_extend_n_merge():
    if bedfile==None:
        tk.messagebox.showinfo('Error','Please import the bed file first')
        return 0
    if not set_ExtendEntry():
        return 0
    if not os.path.isfile(bedfile):
        tk.messagebox.showinfo("Error",f"Error accessing bedfiile {bedfile}\nPlease reimport")
        return 0
    # merge and set annotations
    newfile=mergebedwithAnnotations(bedfile,fixanno=True,extend=ExtendValue,outputfile=False)
    tk.messagebox.showinfo("Complete",f"Merged file created with {ExtendValue}bp extention\n\t{newfile}")

    

#worflow def
def mergebedwithAnnotationfolder(inputfolder,fixanno=True):
    outputfolder=inputfolder+"_merged"
    files=[i for i in os.listdir(inputfolder) if i.endswith(".bed") ]
    try:
        shutil.rmtree(outputfolder)
    except Exception as e:
        #print("Error:",e)
        pass
    os.mkdir(outputfolder)
    for f in files:
        inputfile=inputfolder+os.path.sep+f
        outputfile=outputfolder + os.path.sep + f[:-4]+"_mergedEntries.bed"
        mergebedwithAnnotations(inputfile, fixanno, outputfile)
    print(f"Complete folder")




def mergebedwithAnnotations(inbedfile,fixanno=True,extend=0,outputfile=False):
    bed_entries_perchr,chrlist=readBed2dict(inbedfile)
    outputfilename=inbedfile[:-4]+"_mergedEntris.bed"
    if extend >0:
        outputfilename=inbedfile[:-4]+"_Extend_"+str(extend)+"_mergedEntris.bed"
    if outputfile==False:
        fo=open(outputfilename,"w")
    else:
        fo=open(outputfile,'w')
    for chrom in chrlist:
        merged_annotations=merge_entries(extend_entries(bed_entries_perchr[chrom],extend))
        for start,stop,annotation in merged_annotations:
            fo.write(f"{chrom}\t{start}\t{stop}")
            annotation=fix_annotation(annotation,fixanno)
            if not annotation == "":fo.write(f"\t{annotation}")
            fo.write("\n")
    fo.close()
    if outputfile:
        return outputfile
    else:
        return outputfilename

#function def

def fix_annotation(annotation,fixanno):
    if fixanno == False: return annotation
    anno_items=",".join(annotation.split("|")).split(",")
    unique_annotations=[]
    for item in anno_items:
        if not item in unique_annotations:unique_annotations.append(item)
    return ",".join(unique_annotations)



def readBed2dict(infile):
    chrlist=[]
    entries={}
    fi=open(infile)
    for line in fi:
        if line.startswith("track"):continue
        if line.startswith("browser"):continue
        sline=line.strip().split("\t")
        chrom=sline[0]
        start=int(sline[1])
        stop=int(sline[2])
        annotation=""
        if sline[3]:annotation=sline[3]
        if not chrom in chrlist:
            chrlist.append(chrom)
            entries[chrom]=[]
        entries[chrom].append([start,stop,annotation])
    fi.close()
    #sort chromosome
    for chrom in chrlist : entries[chrom].sort()
    return (entries,chrlist)

def merge_annotations(ann1,ann2):
    items2merge=[]
    if not ann1=="":
        if not ann1 in items2merge:items2merge.append(ann1)
    if not ann2=="":
        if not ann2 in items2merge:items2merge.append(ann2)
    return "|".join(items2merge)



def merge_entries(regionlist):
    newlist=[]
    newlist.append(regionlist[0])
    regioncount=0
    for start,stop,annotation in regionlist:
        regioncount+=1
        if regioncount==1:continue
        if start >newlist[-1][1]:
            newlist.append([start,stop,annotation])
            continue
        #update the last entry
        newlist[-1][0]=min(newlist[-1][0],start)
        newlist[-1][1]=max(newlist[-1][1],stop)
        newlist[-1][2]=merge_annotations(newlist[-1][2],annotation)
    return (newlist)

def extend_entries(regionlist,extend):
    newlist=[]
    for start,stop,annotation in regionlist:
        start -= extend
        stop += extend
        newlist.append([start,stop,annotation])
    return newlist

#UI

root=tk.Tk()
root.title("Extend Merge Bed files")

# Top frame holds title etc.
topframe=tk.Frame(root,height=30,pady=5,padx=5)
topframe.pack(expand="YES",fill='both')

topframe_Title=tk.Label(topframe,text="Extend and Merge Bed files")
topframe_Title.pack()


#Extend frame
extendFrame=tk.Frame(root,height=30,pady=5,padx=5)
extendFrame.pack(expand="YES",fill='both')
extendLabel=tk.Label(extendFrame,text="Extend (bp): ")
extendLabel.pack(side='left')
extendEntry=tk.Entry(extendFrame)
extendEntry.pack(side="left")
extendEntry.insert(0,"0")

#Bed frame
bedframe=tk.Frame(root,height=30,pady=5,padx=5)
bedframe.pack(expand="YES",fill='both')
bed_button=tk.Button(bedframe,text="Import bed file",command=get_bedfile)
bed_button.pack(side='left')
bed_text=tk.Text(bedframe,height=1,width=100)
bed_text.pack(side='left')
bed_text.insert('end',"None")
bed_text.config(state='disabled')

#apply extension

apply_bedextentionandmerge=tk.Button(root,text="Apply ExtendAndMerge",command=apply_extend_n_merge)
apply_bedextentionandmerge.pack()

#help text
help_frame=tk.Frame(root,pady=30,padx=5)
help_frame.pack(expand="YES",fill='both')
#help_text=tk.Label(help_frame,text="This script take expands the bed file and merges the overlapping regions afterwards. It assumed the bed file is sorted, therefore take the chroms as in the order in the bed file.",justify='left')
help_text=tk.Label(help_frame,text="This script take expands the bed file and merges the overlapping regions afterwards. It assumes the bed file is sorted, therefore take the chroms as in the order in the bed file.",wraplength=600,justify='left')
help_text.pack()

root.mainloop()
