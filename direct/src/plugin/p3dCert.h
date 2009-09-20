// Filename: p3dCert.h
// Created by:  drose (11Sep09)
//
////////////////////////////////////////////////////////////////////
//
// PANDA 3D SOFTWARE
// Copyright (c) Carnegie Mellon University.  All rights reserved.
//
// All use of this software is subject to the terms of the revised BSD
// license.  You should have received a copy of this license along
// with this source code in a file named "LICENSE."
//
////////////////////////////////////////////////////////////////////

#ifndef P3DCERT_H
#define P3DCERT_H

#include "wx/wx.h"

#define OPENSSL_NO_KRB5
#include "openssl/x509.h"
#include "openssl/x509_vfy.h"
#include "openssl/pem.h"

#include <string>
#include <iostream>
#include <stdio.h>
using namespace std;

class ViewCertDialog;

////////////////////////////////////////////////////////////////////
//       Class : P3DCertApp
// Description : This is the wxApp that drives this application.
////////////////////////////////////////////////////////////////////
class P3DCertApp : public wxApp {
public:
  virtual bool OnInit();
  virtual void OnInitCmdLine(wxCmdLineParser &parser);
  virtual bool OnCmdLineParsed(wxCmdLineParser &parser);

private:
  wxString _cert_filename;
  wxString _cert_dir;
};

////////////////////////////////////////////////////////////////////
//       Class : AuthDialog
// Description : This is the primary dialog of this application.
//
//               This dialog is presented to the user when he/she
//               clicks on the red authorization button on the splash
//               window.  It tells the user the status of the
//               application's signature, and invites the user to
//               approve the signature or cancel.
////////////////////////////////////////////////////////////////////
class AuthDialog : public wxDialog {
public:
  AuthDialog(const wxString &cert_filename, const wxString &cert_dir);
  virtual ~AuthDialog();

  void run_clicked(wxCommandEvent &event);
  void view_cert_clicked(wxCommandEvent &event);
  void cancel_clicked(wxCommandEvent &event);

  void approve_cert();

private:
  void read_cert_file(const wxString &cert_filename);
  void get_friendly_name();
  void verify_cert();

  void layout();
  void get_text(wxString &header, wxString &text);

public:
  ViewCertDialog *_view_cert_dialog;

private:
  // any class wishing to process wxWidgets events must use this macro
  DECLARE_EVENT_TABLE()

  wxString _cert_dir;
  X509 *_cert;
  STACK *_stack;

  wxString _friendly_name;
  int _verify_result;
};

////////////////////////////////////////////////////////////////////
//       Class : ViewCertDialog
// Description : This is the detailed view of the particular
//               certificate.
////////////////////////////////////////////////////////////////////
class ViewCertDialog : public wxDialog {
public:
  ViewCertDialog(AuthDialog *auth_dialog, X509 *cert);
  virtual ~ViewCertDialog();

  void run_clicked(wxCommandEvent &event);
  void cancel_clicked(wxCommandEvent &event);

private:
  void layout();

private:
  DECLARE_EVENT_TABLE()

  AuthDialog *_auth_dialog;
  X509 *_cert;
};

#endif