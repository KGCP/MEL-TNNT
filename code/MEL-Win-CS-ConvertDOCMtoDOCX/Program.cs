/********************************************************************
# Metadata Extraction & Loader (MEL).
# Author: Sergio.
# Purpose: Utilities for the metadata extraction process.
# Project: AGRIF.
# Last update: 2019-10-01.
********************************************************************/

using System;
using System.IO;
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using Newtonsoft.Json;

namespace MEL
{
    class Utils
    {
        // Given a .docm file (with macro storage), remove the VBA 
        // project, reset the document type, and save the document with a new name.
        public static string ConvertDOCMtoDOCX(string fileName)
        {
            bool fileChanged = false;

            using (WordprocessingDocument document =
                WordprocessingDocument.Open(fileName, true))
            {
                // Access the main document part.
                var docPart = document.MainDocumentPart;

                // Look for the vbaProject part. If it is there, delete it.
                var vbaPart = docPart.VbaProjectPart;
                if (vbaPart != null)
                {
                    // Delete the vbaProject part and then save the document.
                    docPart.DeletePart(vbaPart);
                    docPart.Document.Save();
                }
                {
                    // Change the document type to
                    // not macro-enabled.
                    document.ChangeDocumentType(
                        WordprocessingDocumentType.Document);

                    // Track that the document has been changed.
                    fileChanged = true;
                }
            }

            string newFileName = @"";

            // If anything goes wrong in this file handling,
            // the code will raise an exception back to the caller.
            if (fileChanged)
            {
                // Create the new .docx filename.
                newFileName = Path.ChangeExtension(fileName, ".docx");

                // If it already exists, it will be deleted!
                if (File.Exists(newFileName))
                {
                    File.Delete(newFileName);
                }

                // Rename the file.
                File.Move(fileName, newFileName);
            }
            return newFileName;
        }

        public static string getTempFolder()
        {
            const string jsonFilePath = @"E:\Dropbox\Library\_Eclipse\Workspace\anu-cecs\AGRIF_Project\Loader-to-Document-Store\MEL\config.json";
            string json = File.ReadAllText(jsonFilePath);
            JsonTextReader reader = new JsonTextReader(new StringReader(json));
            bool foundKey = false;
            string tempFolder = @"";
            while (reader.Read() && !foundKey)
            {
                if (foundKey = (reader.TokenType.ToString() == @"PropertyName") && (reader.Value.ToString() == @"Temp-Folder"))
                {
                    reader.Read(); // reads next token:
                    tempFolder = reader.Value.ToString(); // @"E:\_temp\DepFin-Project\_tmp\";
                }
            }
            return tempFolder;
        }

        public static string copyFileToTemp(string inputFilename, string tempDir)
        {
            // Use the Path.Combine method to safely append the file name to the path.
            // Will overwrite if the destination file already exists.
            string fName = Path.GetFileName(inputFilename);
            string tempFilename = Path.Combine(tempDir, fName);
            File.Copy(inputFilename, tempFilename, true);
            Console.WriteLine("* TEMP: " + tempFilename);
            return tempFilename;
        }

        static void Main(string[] args)
        {
            Console.WriteLine("ConvertDOCMtoDOCX <pathfile>");
            switch (args.Length)
            {
                case 0:
                    Console.WriteLine("--> The utility expects one argument: <path to the .docm file to convert>");
                    return;
                case 1:
                    break;
                default:
                    Console.WriteLine("--> {0} arguments are detected; only the first will be taken as a proper input.", args.Length);
                    for (int i = 0; i < args.Length; i++)
                        Console.WriteLine("args[{0}]={1}", i, args[i]);
                    break;
            }
            Console.WriteLine("* INPUT: " + args[0]);
            string outputFilename = ConvertDOCMtoDOCX( copyFileToTemp(args[0], getTempFolder()) );
            Console.WriteLine("* OUTPUT: " + outputFilename);
        }
    }
}
