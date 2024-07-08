import React, { useState, useEffect, useRef } from "react";
import SortableTree, {
  addNodeUnderParent,
  removeNodeAtPath,
  changeNodeAtPath,
  toggleExpandedForAll
} from "@nosferatu500/react-sortable-tree";
import '../../../public/styles/tree_structure.css'
import '../../../public/styles/tree.css';
import AddSVG from '../SVGs/AddSVG.jsx';
import DeleteSVG from '../SVGs/DeleteSVG.jsx';
import EditSVG from "../SVGs/EditSVG.jsx";
import PreviousSVG from "../SVGs/PreviousSVG.jsx";
import NextSVG from "../SVGs/NextSVG.jsx";
import EditButton from "./treeCompmonents/EditButton.jsx";
import AddButton from "./treeCompmonents/AddButton.jsx";
import DeleteButton from "./treeCompmonents/DeleteButton.jsx";
import PersonalTreeSwitch from "./treeCompmonents/PersonalTreeSwitch.jsx";


function Tree({API_URL, isPersonalTree}) {

  const [searchString, setSearchString] = useState("");
  const [searchFocusIndex, setSearchFocusIndex] = useState(0);
  const [searchFoundCount, setSearchFoundCount] = useState(null);
  const [treeData, setTreeData] = useState({});
  const [isEditing, setIsEditing] = useState(false);
  const nodeRefs = useRef({});
  const [oldName, setOldName] = useState(null);
  const [prevTreeData, setPrevTreeData] = useState(null);
  const [lastAddedNodeId, setLastAddedNodeId] = useState(null);
  const [personalNodes, setPersonalNodes] = useState([]);
  const [combinedTree, setCombinedTree] = useState(false);

  useEffect(() => {
    async function fetchData(){
        await fetch(`${API_URL}/json_tree`, {
            method: 'GET',
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            }
        })
        .then(response => response.json())
        .then(data => {
          if(combinedTree || !isPersonalTree){
            setTreeData(data.tree);
            setPrevTreeData(data.tree)
          }else{
            setTreeData(data.personal_tree);
            setPrevTreeData(data.personal_tree)
            setPersonalNodes(data.personal_nodes_id[0]);
          }
        })
        .catch(error => console.error('Error:', error));
    }
    fetchData();
  }, [combinedTree]); 

  useEffect(() => {
    if(lastAddedNodeId === null){
      return;
    }

    // Delay function execution until after the component has finished rendering
    setTimeout(() => {
      const newNodeRef = nodeRefs.current[lastAddedNodeId];
      if(newNodeRef && newNodeRef.current) {
        newNodeRef.current.focus(); 
      }
    }, 0);
  }, [lastAddedNodeId]); // Add lastAddedNodeId as a dependency

  function updateNode(rowInfo) {
    const { node, path } = rowInfo;
    const { title } = node;
    const { children } = node;

    const nodeID = node.id;

    let newTree = changeNodeAtPath({
        treeData,
        path,
        getNodeKey,
        newNode: {
            children,
            title: title,
            id: nodeID
        }
    });

    setTreeData(newTree);
  }

  function tryToPersistNewTitleOrRevertToOld(rowInfo) {

    const newTitle = rowInfo.node.title;
    const nodeID = rowInfo.node.id;

    fetch(`${API_URL}/update_node/${nodeID}/${newTitle}`, {
        method: 'PUT'
    })
    .then(response => response.json())
    .then(data => { 
      if(data.status !== 200){
        revertNodeTitleToOld(rowInfo);
      }
    });
  }

  function revertNodeTitleToOld(rowInfo) {
    rowInfo.node.title = oldName;
    updateNode(rowInfo);
  }

  function tryToPersistNodeMovement(nodeID, parentNodeID){
    fetch(`${API_URL}/move_node/${nodeID}/${parentNodeID}`,{
        method: 'PUT'
    })
    .then(response => response.json())
    .then(data => { 
        if(data.status !== 200){
          setTreeData(prevTreeData);
        }
    });
  }

  function addNodeChild(rowInfo) {
    let { path } = rowInfo;
    const parentNodeID = rowInfo.node.id;
    const value = " ";

    return fetch(`${API_URL}/add_node/${value}/${parentNodeID}`,{
        credentials: "include",
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => { 
        if(data.status === 200){
          if(isPersonalTree && combinedTree){
            let new_nodes = []; 
            data.nodos_dependientes[0].forEach(node => {
              if(!personalNodes.includes(node)){
                new_nodes.push(node);
              }
            });
            setPersonalNodes(personalNodes.concat(new_nodes));
          }else{
            addNodeToTree(rowInfo, value, data.nodoID);
          }
        }
      });
  }

  function addNodeToTree(rowInfo, title, nodoID){
    let { path } = rowInfo;

    let newTree = addNodeUnderParent({
      treeData: treeData,
      parentKey: path[path.length - 1],
      expandParent: true,
      getNodeKey,
      newNode: {
        title: title,
        id: nodoID 
      }
    });
    setLastAddedNodeId(nodoID);
    setIsEditing(true);
    setTreeData(newTree.treeData);
  }


  //Crear un tree temporal y agregar los nodos hijos del nodo seleccionado, luego actualizar el treeData con este nuevo árbol

  // Function to check if a node is already in the tree
  const isNodeInTree = (node, nodes) => {
    for (let i = 0; i < nodes.length; i++) {
      if (nodes[i].id === node.id) {
        return true; // Node found
      }
      // If the current node has children, search recursively in its children
      if (nodes[i].children && isNodeInTree(node, nodes[i].children)) {
        return true; // Node found in children
      }
    }
    return false; // Node not found
  };

  const onEditClicked = (node) => {
    setOldName(node.title);
    setIsEditing(true);
  }

  function removeNode(rowInfo) {
    fetch(`${API_URL}/delete_node/${rowInfo.node.id}`,{
      credentials: "include",
      method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => { 
        if(data.status === 200){
            const { path } = rowInfo;
            if(isPersonalTree && combinedTree){
              const dependentNodes = getDependentNodesID(rowInfo.node);
              setPersonalNodes(personalNodes.filter(node => !dependentNodes.includes(node)));
            }else{
              setTreeData(
                  removeNodeAtPath({
                    treeData,
                    path,
                    getNodeKey
                  })
                );
            }
        }
     })
  }

  function getDependentNodesID(node) {
    let dependentNodes = [node.id];

    function traverseChildren(node) {
      if (node.children) {
        node.children.forEach(child => {
          dependentNodes.push(child.id); 
          traverseChildren(child); 
        });
      }
    }

    traverseChildren(node);

    return dependentNodes;
  }


  function updateTreeData(treeData) {
    setTreeData(treeData);
  }

  function expand(expanded) {
    setTreeData(
      toggleExpandedForAll({
        treeData,
        expanded
      })
    );
  }

  function expandAll() {
    expand(true);
  }

  function collapseAll() {
    expand(false);
  }

  const selectPrevMatch = () => {
    setSearchFocusIndex(
      searchFocusIndex !== null
        ? (searchFoundCount + searchFocusIndex - 1) % searchFoundCount
        : searchFoundCount - 1
    );
  };

  const selectNextMatch = () => {
    setSearchFocusIndex(
      searchFocusIndex !== null ? (searchFocusIndex + 1) % searchFoundCount : 0
    );
  };

  const getNodeKey = ({ treeIndex }) => {
    return treeIndex
  };

  function getInputWidth(length){
    return length * 1.2 + 1;
  }

  function onPersonalTreeSwitchToggled(){
    collapseAll(); 
    if(combinedTree){
      setCombinedTree(false);
    }else{
      setCombinedTree(true);
    }
  }

  function isNodeInsidePersonalTreeAndNotPersonalNode(isPersonalTree, combinedTree, personalNodes, nodeID) {
      return isPersonalTree && combinedTree && !personalNodes.includes(nodeID);
  }

  return (
    <div className="controlsAndTreeDiv">
      <div className="controlsDiv" >
        <div className="expandButtonsDiv">
          <button className="expandButton" onClick={expandAll}>Expand All</button>
          <button className="expandButton" onClick={collapseAll}>Collapse All</button>
        </div>
        <form className="searchForm"
          onSubmit={(event) => {
            event.preventDefault();
          }}
        >
          <label htmlFor="find-box" className="searchLabel">
            Search:&nbsp;
            <input className="searchInput"
              id="find-box"
              type="text"
              value={searchString}
              onChange={(event) => setSearchString(event.target.value)}
            />
          </label>

          <div className="searchButtonsDiv">
            <button
              className="searchButton"
              type="button"
              onClick={selectPrevMatch}
            >
              <PreviousSVG/>
            </button>

            <button
              className="searchButton"
              type="submit"
              onClick={selectNextMatch}
            >
              <NextSVG/>
            </button>
          </div>

          <span>
            &nbsp;
            {searchFoundCount > 0 ? searchFocusIndex + 1 : 0}
            &nbsp;/&nbsp;
            {searchFoundCount || 0}
          </span>
        </form>

        <PersonalTreeSwitch isPersonalTree={isPersonalTree} switchToggled={onPersonalTreeSwitchToggled}/>

      </div>

      <div className="divTree">
        <SortableTree
          rowHeight={55}
          treeData={treeData}
          onChange={(newTreeData) => {
            updateTreeData(newTreeData)
          }}
          onMoveNode={({ node, nextParentNode, path }) => {
            tryToPersistNodeMovement(node.id, nextParentNode.id);
          }}
          canDrop={({ nextParent }) => !!nextParent}
          onDragStateChanged={({isDragging}) => {
            if (isDragging) {
              setPrevTreeData(treeData);
            }
          }}
          searchQuery={searchString}
          searchFocusOffset={searchFocusIndex}
          searchFinishCallback={(matches) => {
            setSearchFoundCount(matches.length);
            setSearchFocusIndex(
              matches.length > 0 ? searchFocusIndex % matches.length : 0
            );
          }}
          canDrag={({ node }) => !node.dragDisabled && !isPersonalTree}
          generateNodeProps={(rowInfo) => {

            if (!nodeRefs.current[rowInfo.node.id]) {
                nodeRefs.current[rowInfo.node.id] = React.createRef();
            }

            const isNodeDisabled = () => {
              return isNodeInsidePersonalTreeAndNotPersonalNode(isPersonalTree, combinedTree, personalNodes, rowInfo.node.id);
            }

            const handleNodeClick = () => {
              if(isNodeDisabled()){
               addNodeChild(rowInfo); 
              }
            };

            return {
            className: isNodeDisabled() ? "hoverNode" : "",
            title: (
                <input className="nodeInput"
                style={{ width: `${getInputWidth(rowInfo.node.title.length)}ch` }}
                ref={nodeRefs.current[rowInfo.node.id]}
                value={rowInfo.node.title}
                readOnly={!isEditing}
                onMouseDown={(event) => event.stopPropagation()}
                onBlur={(event) => {
                    tryToPersistNewTitleOrRevertToOld(rowInfo);

                    setIsEditing(false);
                }}
                onChange={(event) => {
                    const newTitle = event.target.value;

                    updateNode({ ...rowInfo, node: { ...rowInfo.node, title: newTitle } });

                    nodeRefs.current[rowInfo.node.id].current.style.width = `${getInputWidth(event.target.value.length)}ch`;
                }}
                />
            ),
            buttons: [
              <div className="divButtons">
                <AddButton rowInfo={rowInfo} onAddClicked={addNodeChild} isPersonalTree={isPersonalTree}/>
                <EditButton isPersonalTree={isPersonalTree} node={rowInfo.node} nodeRef={nodeRefs.current[rowInfo.node.id]} onEditClicked={onEditClicked}/>
                <DeleteButton rowInfo={rowInfo} removeNode={removeNode} isPersonalTree={isPersonalTree} combinedTree={combinedTree} personalNodes={personalNodes}/>
              </div>
            ],
            style: {
              opacity: isNodeDisabled() ? 0.5 : 1
            },
            onClick: handleNodeClick
          }}}
        />
      </div>
    </div>
  );
}

export default Tree;
