import React, {useEffect, useState} from 'react';
import {useDropzone} from 'react-dropzone';
import '../../../public/styles/dragzone.css';
import '../../../public/styles/cargarAnimacion.css'
import FileZone from './FileZone';
import * as PDFJS from 'pdfjs-dist/legacy/build/pdf';
import 'pdfjs-dist/legacy/build/pdf.worker';
import { toast } from 'react-toastify';

PDFJS.GlobalWorkerOptions.workerSrc = 'pdfjs-dist/legacy/build/pdf.worker.js';
const apiUrl = import.meta.env.PUBLIC_REACT_APP_BACKEND_URL;

function getFileExtension(file) {
  const parts = file.name.split('.');
  return parts[parts.length - 1];
}

function FileValidator(file){
  if(file.type !== 'application/pdf' && file.type !== 'text/plain'){
    return{
      code: 'fileType',
      message: `Fichero \.${getFileExtension(file)} no permitido`
    }
  }
}

function Dropzone(props) {
  const [myAcceptedFiles, setMyAcceptedFiles] = useState([]);
  const [uploading , setUploading] = useState(false);

  const {getRootProps, getInputProps, open, acceptedFiles,fileRejections, isDragActive} = useDropzone({
    maxFiles: 1,
    noClick: true,
    noKeyboard: true,
    onDrop: acceptedFiles => {
      setMyAcceptedFiles(acceptedFiles);
    }, 
    validator: FileValidator
  });

  const deleteFile = (path) => {
    setMyAcceptedFiles(currentFiles => currentFiles.filter(file => file.path !== path));
  }

  const subirFicheroSeleccionardo = async () => {
    const file = myAcceptedFiles[0];
    let fileContent = "";

    if (file.type === 'text/plain') {
      fileContent = await leerFicheroDeTexto(file);
    } else if (file.type === 'application/pdf') {
      fileContent = await leerFicheroPDF(file);
    }

    uploadPersonalTreeWithFile(fileContent);
  };

  const leerFicheroDeTexto = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = function(event) {
        resolve(event.target.result);
      };
      reader.onerror = function(event) {
        reject("File could not be read! Code " + event.target.error.code);
      };
      reader.readAsText(file, "UTF-8");
    });
  };

  function leerFicheroPDF(file) {
    return new Promise((resolve, reject) => {
      if (!(file instanceof Blob)) {
        reject("The provided file is not a Blob or File.");
        return;
      }

      const reader = new FileReader();
      reader.onload = async function(event) {
        const arrayBuffer = event.target.result;

        try {
          const pdf = await pdfjsLib.getDocument({data: arrayBuffer}).promise;
          let totalPageCount = pdf.numPages;
          let countPromises = [];

          for (let currentPage = 1; currentPage <= totalPageCount; currentPage++) {
            let pagePromise = pdf.getPage(currentPage).then(page => {
              return page.getTextContent().then(text => {
                return text.items.map(s => s.str).join('');
              });
            });
            countPromises.push(pagePromise);
          }

          const pagesText = await Promise.all(countPromises);
          resolve(pagesText.join('\n'));
        } catch (reason) {
          reject(reason);
        }
      };
      reader.onerror = function(event) {
        reject("File could not be read! Code " + event.target.error.code);
      };

      reader.readAsArrayBuffer(file);
    });
  }

  const uploadPersonalTreeWithFile = async (fileContent) => {
    setUploading(true);
    fetch(`${apiUrl}/api/personal/upload_tree_from_cv`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        cv: fileContent
      })
    }).then(response => {
      setUploading(false);
      if (response.ok) {
        toast.success('🤖 Conocimientos actualizados', {
          theme: "dark",
          position: "top-center",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: false,
          draggable: true,
          progress: undefined,
        });
      }
    });  
  }
  
  const notify = () => {
  }

  return (
    <>
      <div className='dropZoneDiv'>
        <div className='dropzoneWrapper'>
            <div {...getRootProps({className: `dropzone ${isDragActive ? 'activeDrag' : 'inactiveDrag'}`})}>
            <input {...getInputProps()} />
            <svg fill="none" className='uploadSVG' width="100px" height="100px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M12 8L12 16" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path> <path d="M15 11L12.087 8.08704V8.08704C12.039 8.03897 11.961 8.03897 11.913 8.08704V8.08704L9 11" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path> <path d="M3 15L3 16L3 19C3 20.1046 3.89543 21 5 21L19 21C20.1046 21 21 20.1046 21 19L21 16L21 15" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path> </g></svg>
            <p>Arrastra y suelta los ficheros</p>
            <p>o</p>
            <button className='selectFileButton' type="button" onClick={open}>
              Seleccionar
            </button>
          </div>
        </div>
        <FileZone myAcceptedFiles={myAcceptedFiles} deleteFile={deleteFile} fileRejections={fileRejections}/>
        <div className='subirButtonDiv' >
        {uploading ? <div className='loader'></div> : 
          <button className='subirButton' disabled={!myAcceptedFiles || myAcceptedFiles.length === 0} onClick={subirFicheroSeleccionardo}>
            Subir
          </button>
        }
        </div>
      </div>
    </>
  );
}
export default Dropzone;
