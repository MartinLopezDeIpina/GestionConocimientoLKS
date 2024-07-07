import DeleteSVG from "../../SVGs/DeleteSVG";

const DeleteButton = ({rowInfo, removeNode, isPersonalTree, combinedTree, personalNodes}) => {
	return (
		isParentNode(rowInfo) || isNodeInsidePersonalTreeAndNotPersonalNode(isPersonalTree, combinedTree, personalNodes, rowInfo) ? null : (
			<button className="buttonNode" aria-label="Delete" onClick={() => removeNode(rowInfo)}>
				<DeleteSVG/>
			</button>
		)
	);
}

function isParentNode(rowInfo) {
    return rowInfo.parentNode == null;
}

function isNodeInsidePersonalTreeAndNotPersonalNode(isPersonalTree, combinedTree, personalNodes, rowInfo) {
    return isPersonalTree && combinedTree && !personalNodes.includes(rowInfo.node.id);
}

export default DeleteButton;