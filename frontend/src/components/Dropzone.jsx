import React, {useState} from 'react';
import {useDropzone} from 'react-dropzone';
import '../../public/styles/dragzone.css';
import PDFIcon from './SVGs/PDFIcon';
import TextIcon from './SVGs/TextIcon';
import XSVG from './SVGs/XSVG';
import DeleteSVG from './SVGs/DeleteSVG';



function Dropzone(props) {
  const [myAcceptedFiles, setMyAcceptedFiles] = useState([]);

  const {getRootProps, getInputProps, open, acceptedFiles,fileRejections, isDragActive} = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    noClick: true,
    noKeyboard: true,
    onDrop: acceptedFiles => {
      setMyAcceptedFiles(acceptedFiles);
    }
  });


  const fileRejectionItems = fileRejections.map(({ file, errors }) => (
    <li key={file.path}>
      {file.path} - {file.size} bytes
      <ul>
        {errors.map(e => (
          <li key={e.code}>{e.message}</li>
        ))}
      </ul>
    </li>
  ));

  const deleteFile = (path) => {
    setMyAcceptedFiles(currentFiles => currentFiles.filter(file => file.path !== path));
  }


  return (
    <>
      <div className="container">
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
        <aside>
          <div className='acceptedFilesDiv'>
              {myAcceptedFiles.map(file => (
                  <div className='fileCard' key={file.path}>
                    {file.type === 'application/pdf' ? <PDFIcon/> : <TextIcon/>}
                    <div className='divInfoFile'>
                      <div>
                        {file.path}
                      </div>
                      <div>
                        {file.size} bytes
                      </div>
                    </div>
                    <button className='deleteFileButton' onClick={() => deleteFile(file.path)}>
                      <XSVG />
                    </button>
                  </div>
              ))}
          </div>
          <ul>{fileRejectionItems}</ul>
        </aside>
      </div>
    </>
  );
}
export default Dropzone;
