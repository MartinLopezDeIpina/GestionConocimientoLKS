import FileQuestion from "../SVGs/FileQuestion";
import PDFIcon from "../SVGs/PDFIcon";
import TextIcon from "../SVGs/TextIcon";
import WarningSVG from "../SVGs/WarningSVG";
import XSVG from "../SVGs/XSVG";

const FileZone = ({ myAcceptedFiles, deleteFile, fileRejections }) => {

    const errorsArray = fileRejections.map(({file, errors}) => errors).flat();

    const uniqueErrors = errorsArray.reduce((accumulator, error) => {
        const hasError = accumulator.some(accumulatedError => accumulatedError.code === error.code);
        return hasError ? accumulator : [...accumulator, error];
    }, []);

    const fileRejectionItems = uniqueErrors.map((error) => (
        <div className='errorFicheroDiv' key={error.code}>
            <WarningSVG />
            <p>
                {error.code === 'too-many-files' ? 'Sólo se permite un fichero' : error.message}
            </p>
        </div>
    ));

    return (
        //Si hay ficheros rechazados mostrarlos, sino ficheros elegidos, sino mensaje de que no hay ficheros
        <div className='acceptedFilesDiv'>
            {fileRejections.length > 0 ? 
                <div className="erroresFicherosWrapper">
                    <ul className='erroresFicherosDiv'>{fileRejectionItems}</ul>
                </div>
                : myAcceptedFiles.length > 0 ? 
                    myAcceptedFiles.map(file => (
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
                    ))
                    : 
                    <div className='noAcceptedFilesDiv'>
                        <FileQuestion />
                        <h3 className='h3Fondo'>Ningún fichero seleccionado</h3>
                    </div>
            }
        </div>
    );
};
export default FileZone;