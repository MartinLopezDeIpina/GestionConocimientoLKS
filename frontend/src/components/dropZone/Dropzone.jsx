import React, {useState} from 'react';
import {useDropzone} from 'react-dropzone';
import '../../../public/styles/dragzone.css';
import FileZone from './FileZone';

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
          <button className='subirButton' disabled={!myAcceptedFiles || myAcceptedFiles.length === 0}>
            Subir
          </button>
        </div>
      </div>
    </>
  );
}
export default Dropzone;
