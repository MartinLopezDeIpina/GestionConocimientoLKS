import EditSVG from "../../SVGs/EditSVG";

const EditButton = ({isPersonalTree, node, nodeRef, onEditClicked}) => {
	return (
		!isPersonalTree ? (
			<button className="buttonNode prueba"
				label="Edit"
				onClick={(event) => {
					event.stopPropagation();

					onEditClicked(node);
					nodeRef.current.focus();
				}}
			>
			<EditSVG/>
			</button>   
		) : null
	);
}

export default EditButton;