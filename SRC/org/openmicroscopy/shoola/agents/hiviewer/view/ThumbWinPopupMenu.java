/*
 * org.openmicroscopy.shoola.agents.hiviewer.view.ThumbWinPopupMenu
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

package org.openmicroscopy.shoola.agents.hiviewer.view;


//Java imports
import java.awt.Point;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.BorderFactory;
import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;
import javax.swing.JSeparator;
import javax.swing.border.BevelBorder;

//Third-party libraries

//Application-internal dependencies
import org.openmicroscopy.shoola.agents.hiviewer.IconManager;
import org.openmicroscopy.shoola.agents.hiviewer.cmd.AnnotateCmd;
import org.openmicroscopy.shoola.agents.hiviewer.cmd.ClassifyCmd;
import org.openmicroscopy.shoola.agents.hiviewer.cmd.PropertiesCmd;
import org.openmicroscopy.shoola.agents.hiviewer.cmd.ViewCmd;

/** 
 * Pop-up menu for the thumbnail floating windows.
 * The menu is shered among all instances of {@link ThumbWinPopupMenu} and
 * triggers the execution of commands to view an Image's properties, to
 * annotate it, to classify it, or to view it.
 * 
 * @see ThumbWinManager
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
class ThumbWinPopupMenu
    extends JPopupMenu
{

    /** The sole instance. */
    private static ThumbWinPopupMenu    singleton = new ThumbWinPopupMenu();
    
    
    /**
     * Pops up a menu for the specified thumbnail floating window.
     * 
     * @param win The window.  Mustn't be <code>null</code>.
     */
    public static void showMenuFor(ThumbWin win)
    {
        if (win == null) throw new NullPointerException("No window.");
        singleton.currentWin = win;
        singleton.showMenu();
    }
    
    
    /** The window that is currently requesting the menu. */
    private ThumbWin    currentWin;
    
    
    /**
     * Creates a new instance.
     */
    private ThumbWinPopupMenu()
    {
        IconManager im = IconManager.getInstance();
        JMenuItem properties = new JMenuItem("Properties", 
                                  im.getIcon(IconManager.PROPERTIES)),
                  annotate = new JMenuItem("Annotate", 
                                  im.getIcon(IconManager.ANNOTATE)),
                  classify = new JMenuItem("Classify", 
                                  im.getIcon(IconManager.CLASSIFY)),
                  view = new JMenuItem("View", im.getIcon(IconManager.VIEWER));
        setBorder(BorderFactory.createBevelBorder(BevelBorder.RAISED));
        add(properties);
        add(annotate);
        add(classify);
        add(new JSeparator());
        add(view);
        properties.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent ae)
            {
                new PropertiesCmd(currentWin.getDataObject()).execute();
            }
        });
        annotate.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent ae)
            {
                new AnnotateCmd(currentWin.getDataObject()).execute();
            }
        });
        classify.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent ae)
            {
                new ClassifyCmd(currentWin.getDataObject()).execute();
            }
        });
        view.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent ae)
            {
                new ViewCmd(currentWin.getDataObject()).execute();
            }
        });
    }
    
    /**
     * Brings up the menu for the {@link #currentWin}.
     */
    private void showMenu()
    {
        Point p = currentWin.getPopupPoint();
        show(currentWin, p.x, p.y);
    }
    
}
