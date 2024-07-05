import AddSVG from "../../SVGs/AddSVG"; 

const AddButton = ({rowInfo, onAddClicked}) => {
    return (
        <button className="buttonNode"
            label="Add Child"
            onClick={(event) => { 
                onAddClicked(rowInfo);
            }}
        >
            <AddSVG/>
        </button>
    )
}

export default AddButton;