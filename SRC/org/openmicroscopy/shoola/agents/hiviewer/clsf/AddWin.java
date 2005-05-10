/*
 * org.openmicroscopy.shoola.agents.hiviewer.clsf.AddWin
 *
 *------------------------------------------------------------------------------
 *
 *  Copyright (C) 2004 Open Microscopy Environment
 *      Massachusetts Institute of Technology,
 *      National Institutes of Health,
 *      University of Dundee
 *
 *
 *
 *    This library is free software; you can redistribute it and/or
 *    modify it under the terms of the GNU Lesser General Public
 *    License as published by the Free Software Foundation; either
 *    version 2.1 of the License, or (at your option) any later version.
 *
 *    This library is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *    Lesser General Public License for more details.
 *
 *    You should have received a copy of the GNU Lesser General Public
 *    License along with this library; if not, write to the Free Software
 *    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 *------------------------------------------------------------------------------
 */

package org.openmicroscopy.shoola.agents.hiviewer.clsf;


//Java imports
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.Iterator;
import java.util.Set;
import javax.swing.JComponent;
import javax.swing.JFrame;
import javax.swing.JScrollPane;
import javax.swing.JTree;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.TreePath;
import javax.swing.tree.TreeSelectionModel;


//Third-party libraries

//Application-internal dependencies
import org.openmicroscopy.shoola.agents.hiviewer.util.TreeCellRenderer;
import org.openmicroscopy.shoola.env.data.model.CategoryData;
import org.openmicroscopy.shoola.env.data.model.CategoryGroupData;
import org.openmicroscopy.shoola.env.data.model.DataObject;

/** 
 * 
 *
 * @author  Jean-Marie Burel &nbsp;&nbsp;&nbsp;&nbsp;
 * 				<a href="mailto:j.burel@dundee.ac.uk">j.burel@dundee.ac.uk</a>
 * @author  <br>Andrea Falconi &nbsp;&nbsp;&nbsp;&nbsp;
 * 				<a href="mailto:a.falconi@dundee.ac.uk">
 * 					a.falconi@dundee.ac.uk</a>
 * @version 2.2
 * <small>
 * (<b>Internal version:</b> $Revision$ $Date$)
 * </small>
 * @since OME2.2
 */
class AddWin
    extends ClassifierWin
{

    private static final String     ROOT = "Available categories";
    
    /** Root of the tree. */
    private DefaultMutableTreeNode  root;
    
    private JTree                   tree;
    
    
    AddWin(Set availablePaths, JFrame owner)
    {
        super(availablePaths, owner);
        initTree();
        buildTreeNodes();
        buildGUI();
    }

    /** Handle mouse click event. */
    private void onClick(MouseEvent me)
    {
        int row = tree.getRowForLocation(me.getX(), me.getY());
        if (row != -1) {
            tree.setSelectionRow(row);
            DefaultMutableTreeNode node = (DefaultMutableTreeNode)
                        tree.getLastSelectedPathComponent();
            Object usrObj = node.getUserObject();
            if (usrObj instanceof CategoryData) 
                setSelectedCategory((CategoryData) usrObj);
        }
    }

    /** Initializes the JTree. */
    private void initTree()
    {
        tree = new JTree();
        tree.putClientProperty("JTree.lineStyle", "Angled");
        tree.setCellRenderer(new TreeCellRenderer());
        tree.getSelectionModel().setSelectionMode(
                                    TreeSelectionModel.SINGLE_TREE_SELECTION);
        root = new DefaultMutableTreeNode(ROOT);
        DefaultTreeModel dtm = new DefaultTreeModel(root);
        tree.setModel(dtm);
        tree.setShowsRootHandles(true);
        tree.expandPath(new TreePath(root.getPath()));
        //Attach a tree listener.
        tree.addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent e) { onClick(e); }
            public void mouseReleased(MouseEvent e) { onClick(e); }
        });
    }
    
    /**
     * Builds the tree displaying the hierarchy CategoryGroup - Category.
     * @return See above.
     */
    private void buildTreeNodes()
    {
        if (availablePaths.size() == 0) {
            DefaultTreeModel tm = (DefaultTreeModel) tree.getModel();
            tm.insertNodeInto(new DefaultMutableTreeNode("Empty"), root, 
                            root.getChildCount());
            return;
        }
        Iterator i = availablePaths.iterator();
        DataObject data;
        DefaultMutableTreeNode child, parent;
        DefaultTreeModel treeModel = (DefaultTreeModel) tree.getModel();
        while (i.hasNext()) {
            data = (DataObject) i.next();
            parent = new DefaultMutableTreeNode(data);
            treeModel.insertNodeInto(parent, root, root.getChildCount());
            if (data instanceof CategoryGroupData) {
                Iterator j = 
                    ((CategoryGroupData) data).getCategories().iterator();
                while (j.hasNext()) {
                    child = new DefaultMutableTreeNode(j.next());
                    treeModel.insertNodeInto(child, parent, 
                                parent.getChildCount());
                } 
            }
        }
    }
    
    protected String getWinTitle()
    {
        return "Can be classified as";
    }

    protected String getWinNote()
    {
        return "Select the category to classify the image into";
    }

    /** Wraps the tree in a JScrollPane. */
    protected JComponent getClassifPanel()
    {
        return new JScrollPane(tree);
    }

    
}
