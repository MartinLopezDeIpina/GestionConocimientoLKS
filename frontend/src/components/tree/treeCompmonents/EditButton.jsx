import EditSVG from "../../SVGs/EditSVG";

const EditButton = ({node, nodeRef, onEditClicked}) => {
    return (
        <button className="buttonNode"
            label="Edit"
            onClick={(event) => {
                event.stopPropagation();

                onEditClicked(node);
                nodeRef.current.focus();
            }}
        >
        <EditSVG/>
        </button>   
    )
}

export default EditButton;